/*eslint no-unused-vars: 0*/

/*
  Nautilus JS UI

  - create an indexeddb database from database.js
  - displays random articles on load
  - handles search queries
  - handles infinite scroll for search and home (random)

  Dependencies:
    - imported zimwriterfs.js script
    - PouchDB, jQuery, ScrollMagic, videojs, ogvjs, videojs-ogvjs, SugarJS
    - database.js file containing a DATABASE Array of documents.

*/
/* exported Nautilus */
var Nautilus = (function() {
  var defaults;

  Nautilus.name = 'Nautilus';

  defaults = {
    debug: false,
    database_name: 'nautilus_db',
    database_version: 1,
    database_path: 'database.js',
    nb_items_per_page: 10,
    index_database: false,
    index_database_fields: ["ti", "aut"],
    in_zim: IS_IN_ZIM,
    files_prefix: 'files/',
    show_description: true,
    show_author: true,
  };

  function Nautilus(options) {
    this.options = $.extend({}, defaults, options);
    this.db = new PouchDB(this.options.database_name);
    this.doc_count = 0;
    this.list_e = $("#doc-list");
    this.ident = window.location.hash.substring(1);

    this.console = this.options.debug ? console : {
      log() {},
      debug() {},
      warn() {},
      error() {},
    };

    // search related
    this.in_search = false;
    this.search_text = "";
    this.search_cursor = 0;
    this.end_of_results = false;

    // scroll related
    this.scroll_ctrl = new ScrollMagic.Controller();
    this.scroll_scene = null;
  }

  Nautilus.prototype.start = function() {
    this.init_videojs();
    this.init_search();
    this.init_modal();
    this.init_backtotop();
    this.init_database();
  };

  /*** ZIM-RELATED ***/
  Nautilus.prototype.get_image_path = function (filepath) {
    if (this.options.in_zim) {
      return ZIM_IMG_NS + filepath;
    }
    return filepath;
  }

  Nautilus.prototype.get_meta_path = function (filepath) {
    if (this.options.in_zim) {
      return ZIM_META_NS + filepath;
    }
    return filepath;
  }

  Nautilus.prototype.get_file_path = function (filename) {
    return this.get_image_path(this.options.files_prefix + filename);
  }

  Nautilus.prototype.get_database_path = function () {
    return this.get_meta_path(this.options.database_path);
  }

  /*** DATABASE-RELATED ***/
  Nautilus.prototype.on_database_ready = function(db_info) {
    this.doc_count = db_info.doc_count;
    this.console.debug("database ready", this.doc_count, "documents");
    if (this.ident)
      this.restoreState(this.ident);
    else
      this.getRows();
  };

  Nautilus.prototype.index_database = function (db_info) {
    var _this = this;
    _this.db.createIndex({index: {fields: _this.options.index_database_fields}})
      .then(function (result) {
        _this.console.debug("index created", result);
        _this.on_database_ready(db_info);
      }).catch(function (err) {
        _this.console.error("Error creating index for "+ _this.options.index_database_fields +" fields.", err);
      });
  };

  Nautilus.prototype.loadScript = function loadScript(src, callback) {
    var script  = document.createElement("script");
    script.setAttribute("src", src);
    script.addEventListener("load", callback);
    let body = document.getElementsByTagName("body")[0];
    body.insertBefore(script, body.getElementsByTagName("script")[0]);
  };

  Nautilus.prototype.load_database_from_file = function () {
    var _this = this;
    this.loadScript(this.get_database_path(), function(){
      _this.console.debug("database loaded (not imported)");

      const start = Date.now();
      _this.db.bulkDocs(DATABASE)
        .then(() => {
          const end = Date.now();
          _this.console.log('time ran:', (end - start) / 1000, 'seconds');
          
          _this.db.info().then(function (db_info) {
            if (_this.options.index_database) {
              _this.index_database(db_info);
            } else {
              _this.on_database_ready(db_info);
            }
          });
        }).catch(function (err) {
          _this.console.error("Error inserting JS data from "+ _this.options.database_path +" into database.", err);
      });
    });
  };

  Nautilus.prototype.init_videojs = function () {
    videojs.options.controls = true;
    videojs.options.crossorigin = true;
    videojs.options.preload = "auto";
    videojs.options.techOrder = ["html5", "ogvjs"];
    videojs.options.ogvjs = {base: "vendors/ogvjs"};
    // for some reason, global controls options is not working
    window.videojs_options = {controls: true, preload: 'auto', crossorigin: true};
  };

  Nautilus.prototype.init_database = function () {
    var _this = this;
    this.db.info()
      .then(function (db_info) {
        if (db_info.doc_count === 0) {
          _this.load_database_from_file();
        }
        else {
          _this.console.debug("database exists");
          _this.on_database_ready(db_info);
        }
      });
  };

  /*** MODAL-RELATED (audio files) ***/
  /*  register handler on modal close to set a placeholder content
      that would appear on next modal's until it loads */
  Nautilus.prototype.init_modal = function () {
    $('#modal').on('hidden.bs.modal', function () {
      $(".modal-body").html("Chargement…");
    });
  };

  Nautilus.prototype.openAudioPlayer = function(db_id) {
    var _this = this;
    $("#modal h5").text("…");
    $('#modal').modal({backdrop: 'static'});
    this.db.get(db_id).then((db_doc) => {
      // update link
      _this.updateIdent({modalAudioId: db_id});

      $("#modal h5").text(db_doc.ti);
      let body = "";
      let multiple = db_doc.fp.length > 1;
      db_doc.fp.forEach((fname, index) => {
        body += _this.getAudioCode(fname, multiple ? index + 1 : -1) + "\n";
      });
      body += "<script>$('.video-js').each(function(){ videojs($(this)[0], videojs_options)});</script>"
      $('#modal .modal-body').html(body);
    });
  }

  /*  enable search trigger */
  Nautilus.prototype.init_search = function () {
    var _this = this;
    $("form").on("submit", function (e) {
      e.preventDefault();
      _this.search($("#search_text").val().trim());
    });
  }

  Nautilus.prototype.init_backtotop = function () {
    $('.back-to-top').click(function (e) {
      e.preventDefault();
      $('body,html').animate({scrollTop: 0}, 400);
      return false;
    });
  };

  /*** SCROLL ***/
  Nautilus.prototype.init_scroll = function () {
    var _this = this;
    this.scroll_scene = new ScrollMagic.Scene(
        {triggerElement: ".scrollable-content #loader", triggerHook: "onEnter"})
      .addTo(this.scroll_ctrl)
      .on("enter", function () {
        if (!$("#loader").hasClass("active")) {
          // reached bottom
          _this.enableInfiniteScroll();
          _this.getRows();
        }
      });
  }

  /*** UI GEN ***/
  Nautilus.prototype.resetList = function () {
    this.list_e.html("");
  };

  Nautilus.prototype.getAudioCode = function (fname, index) {
    let fpath = this.get_file_path(fname);
    let dl_link = "<a href=\""+ fpath +"\">télécharger</a>";
    let fline;
    if (index == -1)
      fline = "Morceau unique (" + dl_link + ")";
    else
      fline = "Morceau " + index + " (" + dl_link + ")";
    return "<p>" + fline +
      "<audio class=\"video-js vjs-default-skin\" " + 
      "style=\"width: 100%; height: 3em;\">" + 
      "<source src=\"" + fpath + "\" type=\"audio/ogg\" /></audio></p>";
  };

  Nautilus.prototype.getItemFor = function (db_doc) {
    let listElement = $("<li />");

    let extension;
    let linkTarget = "";
    let htmlTarget = "";
    // what kind of link is that?
    if (db_doc.fp.length > 1) {
      // a multiple audio link
      linkTarget = "javascript:nautilus.openAudioPlayer('" + db_doc._id + "');";
      extension = "ogg";
    } else {
      let fp = db_doc.fp[0];
      extension = Sugar.String.reverse(Sugar.String.reverse(fp).split(".")[0]);
      if (extension == "ogg") {
        //  a single audio file
        linkTarget = "javascript:nautilus.openAudioPlayer('" + db_doc._id + "');";
      } else {
        // a regular file to download
        linkTarget = this.get_file_path(fp);
      }
    }

    let icon_src = this.get_image_path("vendors/ext-icons/" + extension + ".svg");

    let elementHTML = "<span class=\"icon\">" + 
      "<a" + htmlTarget + " href=\"" + linkTarget + "\" class=\"btn btn-neutral\">" +
      "<img src=\"" + icon_src + "\" /></a></span>" +
      "<div class=\"info\"><h2 class=\"title\">" + db_doc.ti + "</h2>";

    if (this.options.show_author)
      elementHTML += "<p class=\"small\">" + db_doc.aut + "</p>";

    if (this.options.show_description)
      elementHTML += "<p class=\"desc\">" + db_doc.dsc + "</p>";

    elementHTML += "</div>";
    listElement.html(elementHTML);
    return listElement;
  }

  Nautilus.prototype.displayRows = function (rows) {
    var _this = this;
    rows.forEach((row) => {
      _this.list_e.append(row);
    });
    _this.on_rows_updated();
  };

  Nautilus.prototype.update_sroll_scene = function () {
    if (this.scroll_scene == null)
      this.init_scroll();
    else
      this.scroll_scene.update();
  };

  Nautilus.prototype.enableInfiniteScroll = function () { this.toggleInfiniteScroll(true); }
  Nautilus.prototype.disableInfiniteScroll = function () { this.toggleInfiniteScroll(false); }
  Nautilus.prototype.toggleInfiniteScroll = function (enable) {
    if (enable)
      $("#loader").addClass("active");
    else
      $("#loader").removeClass("active");
  };

  Nautilus.prototype.on_no_search_result = function() {
    this.console.debug("no search result");
    this.disableInfiniteScroll();
    $("#loader").hide();
    $(".no-result").show();
  };

  Nautilus.prototype.on_no_more_search_result = function() {
    this.console.debug("no more search result");
    this.disableInfiniteScroll();
    $("#loader").hide();
  };

  Nautilus.prototype.on_rows_updated = function () {
    this.update_sroll_scene(); // make sure the scene gets the new start position
    this.disableInfiniteScroll();
  };

  Nautilus.prototype.updateIdent = function(update) {
    // update current ident with supplied info and refresh URI
    let pident = this.parsedIdent();
    pident = Sugar.Object.merge(pident, update);

    // serialize ident
    if (pident.kind == "random") {
      options = pident.documentIds.join(".");
    }
    if (pident.kind == "search") {
      options = pident.cursor.toString() + "_" + pident.text.trim();
    }
    this.ident = pident.kind + "-" + pident.modalAudioId + "-" + options;
    window.location.hash = this.ident;
  }

  Nautilus.prototype.resetIdent = function(update) {
    // sets the ident using the provided info
    this.ident = "";
    this.updateIdent(update);
  }

  Nautilus.prototype.parsedIdent = function(ident) {
    // format::  {kind}-{modalAudioId}-{options}
    // rando::   random-{modalAudioId}-{id}.{id}.{id}
    // search::  search-{modalAudioId}-{cursor}_{text}

    if (ident === undefined)
      ident = this.ident;

    let kind = modalAudioId = options = documentIds = cursor = text = "";

    let parts = ident.split("-", 3);
    if (parts.length == 3)
      options = parts.pop();
    if (parts.length == 2)
      modalAudioId = parts.pop();
    kind = parts.pop();

    if (kind == "random") {
      documentIds = options.trim().split(".")
        .map(function (sid) { return parseInt(sid); })
        .filter(function (id) { return !isNaN(id)})
        .map(function (id) { return id.toString();});
    }

    if (kind == "search") {
      let opt_parts = options.split("_", 2);
      cursor = 0;
      text = opt_parts.pop().trim();
      if (opt_parts.length)
        cursor = parseInt(opt_parts.pop().trim()) || 0;
    }

    return {
      'kind': kind,
      'modalAudioId': modalAudioId,
      'options': options,
      'documentIds': documentIds,
      'cursor': cursor,
      'text': text,
    }

  };

  Nautilus.prototype.restoreState = function(ident) {
    this.console.debug("restoring state", ident);
    let pident = this.parsedIdent(ident);

    if (pident.kind == "random") {
      if (pident.documentIds.length) {
        this.getRequestedDocuments("random", pident.documentIds, this.displayRows);
      }
    }
    else if (pident.kind == "search") {
        $("#search_text").val(pident.text);
        this.search(pident.text, pident.cursor);
    } else {
      this.console.debug("invalid ident!");
      this.resetIdent({});
      this.getRows();
    }

    if (pident.modalAudioId) {
      this.console.debug("restoring modal", pident.modalAudioId);
      this.openAudioPlayer(pident.modalAudioId);
    }
  };

  Nautilus.prototype.getRows = function () {
    if (this.in_search) {
      this.getSearchResults(this.search_text, this.displayRows);
    } else {
      this.getRandomDocuments(this.displayRows);
    }
  };

  Nautilus.prototype.getRequestedDocuments = function (ident_prefix, doc_ids, on_complete) {
    var _this = this;
    this.resetIdent({kind: "random", documentIds: doc_ids});
    this.db.allDocs({keys: doc_ids, include_docs: true})
      .then((results) => {
        let rows = [];
        results.rows.forEach(function (row) {
          if (!row.doc) {
            _this.console.error("row", row, "has no doc");
          } else {
            rows.push(_this.getItemFor(row.doc));
          }
        })
        
        if (on_complete) {
          on_complete.apply(_this, [rows]);
        }
        
      }).catch(function (err) {
        _this.console.error("Error in getting documents", doc_ids, err);
      });
  };

  Nautilus.prototype.getRandomDocuments = function (on_complete) {
    var _this = this;
    function getRandomInt(max) {
      return Math.floor(Math.random() * max);
    }

    _this.console.log("displayRandomDocuments", this.doc_count, this.options.nb_items_per_page);
    let seq_ids = [];
    for (var i=0; i<this.options.nb_items_per_page;i++) {
      seq_ids.push(getRandomInt(this.doc_count).toString());
    }
    this.getRequestedDocuments("random", seq_ids, on_complete);
  };

  Nautilus.prototype.getSearchResults = function (text, on_complete) {
    this.console.debug("getting search results for", text);
    var _this = this;
    let query = {
      $or: [
        {ti: {$regex: new RegExp(text, 'i')}},
        {aut: {$regex: new RegExp(text, 'i')}},
      ],
    };
    let skip = _this.search_cursor || 0;
    let findOpts = {selector: query,
                    fields: ['ti', 'dsc', 'aut', 'fp', '_id'],
                    skip: skip,
                    limit: _this.options.nb_items_per_page};

    this.resetIdent({kind: "search", cursor: skip, text: text.trim()});

    this.db.find(findOpts).then(function (result) {
      if (!result || !result.docs || !result.docs.length) {
        _this.on_no_search_result();
        return;
      }
      if (result.docs.length < findOpts.limit) {
        _this.on_no_more_search_result();
      }
      _this.search_cursor += result.docs.length;

      let rows = [];
      result.docs.forEach((doc) => {
        rows.push(_this.getItemFor(doc));
      });

      if (on_complete)
        on_complete.apply(_this, [rows]);
    }).catch(function (err) {
      _this.console.error("Error finding docs for "+ text + ".", err);
    });
  };

  Nautilus.prototype.search = function (text, cursor) {
    this.disableInfiniteScroll();
    $(".no-result").hide();
    $("#loader").show();
    this.search_cursor = cursor || 0;
    this.search_text = text;
    this.in_search = true;
    this.resetList();
    this.getRows();
    this.enableInfiniteScroll();
  }

  return Nautilus;

})();
