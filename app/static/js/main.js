
document.addEventListener("DOMContentLoaded", () => {
  //=== Initialize widgets

  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

function bindEvents() {

  add_class_event('statcard-view', 'click', statcard);


  add_id_event('search-input', 'input', dndsearch);
  add_id_event('category', 'change', dndsearch);

  add_id_event('nav-reference', 'click', referencetab);
  add_id_event('reference-tab-title', 'click', referencetab);

  add_id_event('nav-npc', 'click', npctab);
  add_id_event('npc-tab-title', 'click', npctab);
  add_id_event('generate-npc', 'click', npcgen);

  add_id_event('nav-shop', 'click', shoptab);
  add_id_event('shop-tab-title', 'click', shoptab);
  add_id_event('generate-shop', 'click', shopgen);

  add_id_event('nav-encounter', 'click', encountertab);
  add_id_event('encounter-tab-title', 'click', encountertab);
  add_id_event('generate-encounter', 'click', encountergen);
}

function npcgen() {
  console.log("npcs");
  let loader = document.createElement('div');
  loader.classList.add('is-loading');
  this.parentNode.appendChild(loader);
  get_data("npcs", (data) => {
    setTimeout(() => {
      loader.remove();
      let results = document.getElementById('statblock');
      results.innerHTML = "";
      location.reload();
    }, 30000);
  });
}

function shopgen() {
  console.log("shops");
}

function encountergen() {
  console.log("encounters");
}

function tab_toggle(tabselected) {
  let tabs = get_object_by_id("generator-tabs");
  hide_children(tabs);
  get_children(get_object_by_id("tab-titles")).forEach(el => {
    el.classList.remove('is-active');
  });

  get_object_by_id(`${tabselected}-tab-title`).classList.add('is-active');
  let panel = get_object_by_id(`${tabselected}-tab`);
  show(panel);
  panel.scrollIntoView({
    block: 'start',
    behavior: 'smooth',
    inline: 'start'
  });
}

function referencetab() {
  tab_toggle('reference');
}

function npctab() {
  tab_toggle('npc');
}

function shoptab() {
  tab_toggle('shop');
}

function encountertab() {
  tab_toggle('encounter');
}

function dndsearch() {
  var results = get_object_by_id("search-results");
  results.innerHTML = "";
  let keyword = this.value;
  if (keyword.length > 2) {
    var category = get_object_by_id("category").value;
    post_data("search", { category: category, keyword: keyword }, (data) => {
      results.innerHTML = "";
      data["results"].forEach((el) => {
        let new_entry = get_object_by_id("search-result-item-template").cloneNode(true);
        new_entry.removeAttribute("id");
        new_entry.dataset.pk = el["pk"];
        new_entry.querySelector('a').innerHTML = el["name"];
        console.log(new_entry);
        results.appendChild(new_entry);
        add_event(new_entry, 'click', statcard);
      });
    });
  }
}

function statcard() {
  let pk = this.dataset.pk;
  let category = this.dataset.category;
  post_data("statblock", { pk: pk, category: category }, (data) => {
    let results = document.getElementById('statblock');
    results.innerHTML = "";
    console.log(data);
    if (data["results"]) {
      let div = document.createElement('div');
      div.innerHTML = data["results"];
      results.appendChild(div);
    } else {
      results.innerHTML = "No statblock found";
    }
    // add_class_event('inventory-select', 'change', () => {
    //   get_objects_by_class('item-description').forEach(el => { hide(el); });
    //   //console.log(this.value);
    //   show(document.getElementById(this.value));
    // });
    // add_class_event('spell-select', 'change', () => {
    //   get_objects_by_class('spell-description').forEach(el => { hide(el); });
    //   //console.log(this.value);
    //   show(document.getElementById(this.value));
    // });
    // add_class_event('monster-select', 'change', () => {
    //   get_objects_by_class('feature-description').forEach(el => { hide(el); });
    //   //console.log(this.value);
    //   show(document.getElementById(this.value));
    // });
  });
}

