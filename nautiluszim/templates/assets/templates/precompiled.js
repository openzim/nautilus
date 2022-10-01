(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['display_rows'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "  <li>\n      <span class=\"icon\">\n        <a href=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"target") || (depth0 != null ? lookupProperty(depth0,"target") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"target","hash":{},"data":data,"loc":{"start":{"line":4,"column":17},"end":{"line":4,"column":27}}}) : helper)))
    + "\" data-doc-id=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"docid") || (depth0 != null ? lookupProperty(depth0,"docid") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"docid","hash":{},"data":data,"loc":{"start":{"line":4,"column":42},"end":{"line":4,"column":51}}}) : helper)))
    + "\" data-popup=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"popup") || (depth0 != null ? lookupProperty(depth0,"popup") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"popup","hash":{},"data":data,"loc":{"start":{"line":4,"column":65},"end":{"line":4,"column":74}}}) : helper)))
    + "\" class=\"btn btn-neutral\">\n          <img src=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"icon") || (depth0 != null ? lookupProperty(depth0,"icon") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"icon","hash":{},"data":data,"loc":{"start":{"line":5,"column":20},"end":{"line":5,"column":28}}}) : helper)))
    + "\" />\n        </a>\n      </span>\n      <div class=\"info\">\n        <h2 class=\"title\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":9,"column":26},"end":{"line":9,"column":35}}}) : helper)))
    + "</h2>"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"author") : depth0),{"name":"if","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":9,"column":40},"end":{"line":10,"column":48}}})) != null ? stack1 : "")
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"description") : depth0),{"name":"if","hash":{},"fn":container.program(4, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":10,"column":48},"end":{"line":11,"column":50}}})) != null ? stack1 : "")
    + "\n      </div>\n  </li>\n";
},"2":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "\n        <p class=\"small\">"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"author") || (depth0 != null ? lookupProperty(depth0,"author") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"author","hash":{},"data":data,"loc":{"start":{"line":10,"column":25},"end":{"line":10,"column":37}}}) : helper)))
    + "</p>";
},"4":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "\n        <p class=\"desc\">"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"description","hash":{},"data":data,"loc":{"start":{"line":11,"column":24},"end":{"line":11,"column":39}}}) : helper)))
    + "</p>";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return ((stack1 = lookupProperty(helpers,"each").call(depth0 != null ? depth0 : (container.nullContext || {}),(depth0 != null ? lookupProperty(depth0,"rows") : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":1,"column":0},"end":{"line":14,"column":9}}})) != null ? stack1 : "");
},"useData":true});
templates['media_player'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=container.lambda, alias2=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "  <p><a href=\""
    + alias2(alias1((depth0 != null ? lookupProperty(depth0,"fpath") : depth0), depth0))
    + "\"><img class=\"icon\" src=\""
    + alias2(alias1((depth0 != null ? lookupProperty(depth0,"icon") : depth0), depth0))
    + "\" /> "
    + alias2(alias1((depth0 != null ? lookupProperty(depth0,"fname") : depth0), depth0))
    + "</a>\n  "
    + ((stack1 = lookupProperty(helpers,"if").call(depth0 != null ? depth0 : (container.nullContext || {}),(depth0 != null ? lookupProperty(depth0,"is_file") : depth0),{"name":"if","hash":{},"fn":container.program(2, data, 0),"inverse":container.program(4, data, 0),"data":data,"loc":{"start":{"line":3,"column":2},"end":{"line":6,"column":9}}})) != null ? stack1 : "")
    + "</p>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "";
},"4":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, alias5=container.lambda, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "\n  <"
    + alias4(((helper = (helper = lookupProperty(helpers,"kind") || (depth0 != null ? lookupProperty(depth0,"kind") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"kind","hash":{},"data":data,"loc":{"start":{"line":4,"column":3},"end":{"line":4,"column":11}}}) : helper)))
    + " class=\"video-js vjs-default-skin nautilus-"
    + alias4(((helper = (helper = lookupProperty(helpers,"kind") || (depth0 != null ? lookupProperty(depth0,"kind") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"kind","hash":{},"data":data,"loc":{"start":{"line":4,"column":54},"end":{"line":4,"column":62}}}) : helper)))
    + "\">\n  <source src=\""
    + alias4(alias5((depth0 != null ? lookupProperty(depth0,"fpath") : depth0), depth0))
    + "\" type=\""
    + alias4(alias5((depth0 != null ? lookupProperty(depth0,"mime") : depth0), depth0))
    + "\" /></"
    + alias4(((helper = (helper = lookupProperty(helpers,"kind") || (depth0 != null ? lookupProperty(depth0,"kind") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"kind","hash":{},"data":data,"loc":{"start":{"line":5,"column":56},"end":{"line":5,"column":64}}}) : helper)))
    + ">\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return ((stack1 = lookupProperty(helpers,"each").call(depth0 != null ? depth0 : (container.nullContext || {}),((stack1 = (depth0 != null ? lookupProperty(depth0,"doc") : depth0)) != null ? lookupProperty(stack1,"items") : stack1),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":1,"column":0},"end":{"line":8,"column":9}}})) != null ? stack1 : "");
},"useData":true});
templates['modal_empty_body'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<p>"
    + container.escapeExpression(container.lambda(((stack1 = (depth0 != null ? lookupProperty(depth0,"i18n") : depth0)) != null ? lookupProperty(stack1,"loading") : stack1), depth0))
    + "<p>\n";
},"useData":true});
templates['modal_title'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":1,"column":0},"end":{"line":1,"column":9}}}) : helper)))
    + "\n";
},"useData":true});
})();