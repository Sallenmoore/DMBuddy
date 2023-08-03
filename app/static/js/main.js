
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

  // Nav
  add_id_event('nav-reference', 'click', referencetab);
  add_id_event('reference-tab-title', 'click', referencetab);

  // Reference
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


function getTaskStatus(taskID) {
  console.log(taskID);
  post_data("checktask", { "id": taskID }, res => {
    console.log(res);
    console.log(res.results.task_id);
    console.log(res.results.task_status);
    console.log(res.results.task_results);
    location.reload();
    // if (res.results.task_status != 'SUCCESS' && res.results.task_status != 'FAILURE') {
    //   setTimeout(() => getTaskStatus(res.results.task_id), 2000);
    // }
  });
}

function task(task_name, task_data = {}) {
  let loader = document.createElement('div');
  loader.classList.add('is-loading');
  let statblock = get_object_by_id('statblock');
  statblock.insertBefore(loader, statblock.firstChild);
  task = {};
  task[task_name] = task_data;
  post_data("task", task, (data) => {
    setTimeout(() => getTaskStatus(data.results.results), 30000);
  });
}

function npcgen() {
  task("generateNPC");
}

function shopgen() {
  console.log("shops");
}

function encountergen() {
  console.log("encounters");
}

function imggen() {
  let statblock = this.closest('.statblock');
  let pk = statblock.dataset.pk;
  let category = statblock.dataset.category;
  task("generateImage", { "pk": pk, "category": category });
}

////////////////////////////////////////////////////////////////////////////////

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
        //console.log(new_entry);
        results.appendChild(new_entry);
        add_event(new_entry, 'click', statcard);
      });
    });
  }
}

function statcard() {
  var item = this.closest('.statcard-item');
  let pk = item.dataset.pk;
  let category = item.dataset.category;
  post_data("statblock", { pk: pk, category: category }, (data) => {
    let results = document.getElementById('statblock');
    //console.log(data);
    if (data["results"]) {
      let div = document.createElement('div');
      div.classList.add('column');
      div.classList.add('is-half');
      div.innerHTML = data["results"];
      results.insertBefore(div, results.firstChild);
      add_class_event('generate-image', 'click', imggen);
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