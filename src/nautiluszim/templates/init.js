$( document ).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    window.nautilus = new Nautilus({
        title: "{{ title|safe }}",
        description: "{{ description|safe }}",
        database_name: "{{ db_name }}.{{ db_version }}",
        database_version: "{{ db_version }}",
        nb_items_per_page: {{ nb_items_per_page }},
        show_author: {{ show_author|lower }},
        show_description: {{ show_description|lower }},
        randomize: {{ randomize|lower }},
        debug: {{ debug }},
        i18n: {loading: "{{ loading_label | safe}}",},
    });
    window.nautilus.start();
});
