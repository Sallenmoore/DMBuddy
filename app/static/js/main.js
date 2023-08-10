
document.addEventListener("DOMContentLoaded", () => {
  //=== Initialize widgets

  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

function bindEvents() {
  // General
  add_class_event('statcard-view', 'click', statcard);
  add_id_event('statcard-clear', 'click', () => { get_object_by_id('statblock').innerHTML = ""; });
  add_class_event('item-delete', 'click', deleteitem);

  // Reference
  add_id_event('nav-reference', 'click', referencetab);
  add_id_event('reference-tab-title', 'click', referencetab);
  add_id_event('search-input', 'input', dndsearch);
  add_id_event('category', 'change', dndsearch);

  // NPC
  add_id_event('nav-npc', 'click', npctab);
  add_id_event('npc-tab-title', 'click', npctab);
  add_id_event('generate-npc', 'click', npcgen);

  // Shop
  add_id_event('nav-shop', 'click', shoptab);
  add_id_event('shop-tab-title', 'click', shoptab);
  add_id_event('generate-shop', 'click', shopgen);

  // Encounter
  add_id_event('nav-encounter', 'click', encountertab);
  add_id_event('encounter-tab-title', 'click', encountertab);
  add_id_event('generate-encounter', 'click', encountergen);
}


function getTaskStatus(taskID, iters) {
  console.log(taskID);
  post_data("checktask", { "id": taskID }, res => {
    console.log(res);
    console.log(res.results.task_id);
    console.log(res.results.task_status);
    console.log(res.results.task_results);
    console.log(iters);
    if (iters > 0 && res.results.task_status != 'SUCCESS' && res.results.task_status != 'FAILURE') {
      setTimeout(() => getTaskStatus(taskID, iters - 1), 3000);
    } else {
      get_objects_by_class('is-loading').forEach(el => el.remove());
    }
    console.log(res.results);
  });
}

function task(task_name, task_data = {}) {
  let loader = document.createElement('div');
  loader.classList.add('is-loading');
  let statblock = get_object_by_id('statblock');
  statblock.insertBefore(loader, statblock.firstChild);
  post_data(task_name, task_data, (data) => {
    console.log(data);

    setTimeout(() => getTaskStatus(data.results, 7), 3000);
  });
}

function npcgen() {
  task("npcgen");
}

function shopgen() {
  task("shopgen");
}

function encountergen() {
  task("encountergen");
}

function lootgen() {
  task("lootgen");
}

function imggen() {
  let statblock = this.closest('.statblock');
  let pk = statblock.dataset.pk;
  let category = statblock.dataset.category;
  task("imagegen", { "pk": pk, "category": category });
}

////////////////////////////////////// Tab Toggle //////////////////////////////////////////

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
        new_entry.dataset.category = category;
        new_entry.querySelector('a').innerHTML = el["name"];
        //console.log(new_entry);
        results.appendChild(new_entry);
        add_event(new_entry, 'click', statcard);
      });
    });
  }
}



function updatestats() {
  var form = this.closest('.statblock-form');
  var obj = form_values(this);
  obj['pk'] = this.querySelector('.statblock').dataset.pk;
  obj['category'] = this.querySelector('.statblock').dataset.category;
  console.log(obj);
  post_data("updates", obj, (data) => {
    getstatcard(obj['pk'], obj['category']);
  });
}

function statcard() {
  var item = this.closest('.statcard-item');
  let pk = item.dataset.pk;
  let category = item.dataset.category;
  getstatcard(pk, category);
}

function getstatcard(pk, category) {
  post_data("statblock", { pk: pk, category: category }, (data) => {
    let results = document.getElementById('statblock');
    //console.log(data);
    if (data["results"]) {
      let div = document.createElement('div');
      div.classList.add('column');
      //div.classList.add('is-half');
      div.innerHTML = data["results"];
      results.insertBefore(div, results.firstChild);
      add_class_event('generate-image', 'click', imggen);
      add_class_event('statblock-form', 'change', updatestats);
    } else {
      results.innerHTML = "No statblock found";
    }
  });
}


//////////////////////////////////////////  Delete Items  //////////////////////////////////////////

function deleteitem() {
  var item = this.closest('.statcard-item');
  let pk = item.dataset.pk;
  let category = item.dataset.category;
  post_data("delete", { pk: pk, category: category }, (data) => {
    console.log(data);
    item.remove();
  });
}