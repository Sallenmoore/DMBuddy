document.addEventListener("DOMContentLoaded", () => {
  //=== configure autojs
  // autojs.configure({
  //   textarea_autoheight: true, #default: true
  // });
  //=== Initialize widgets
  new Tab();
  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

function bindEvents() {

  // Statcards
  add_class_event('statcard-view', 'click', statcard);
  add_id_event('statcard-clear', 'click', () => { get_object_by_id('statblock').innerHTML = ""; });
  add_class_event('item-delete', 'click', deleteitem);

  // Reference
  add_id_event('search-input', 'input', dndsearch);
  add_id_event('category', 'change', dndsearch);

  // NPC
  add_id_event('generate-npc', 'click', npcgen);
  add_id_event('update-canon-npc', 'click', update_canon_npc);

  // Shop
  add_id_event('generate-shop', 'click', shopgen);

  // Encounter
  add_id_event('generate-encounter', 'click', encountergen);
}


function getTaskStatus(taskID, iters) {
  var loader = new Loader('statblock');
  post_data("checktask", { "id": taskID }, res => {
    // console.log(res);
    // console.log(res.results.task_id);
    // console.log(res.results.task_status);
    // console.log(res.results.task_results);
    // console.log(iters);
    if (iters > 0 && res.results.task_status != 'SUCCESS' && res.results.task_status != 'FAILURE') {
      setTimeout(() => getTaskStatus(taskID, iters - 1), 3000);
    } else {
      loader.remove();
    }
    //console.log(res.results);
  });
}

function task(task_name, task_data = {}) {
  post_data(task_name, task_data, (data) => {
    //console.log(data);
    setTimeout(() => getTaskStatus(data.results, 7), 100);
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

////////////////////////////////////// AJAX Calls //////////////////////////////////////////


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

function update_canon_npc() {
  get_data("updatecanon", (data) => {
    console.log(data);
  });
}

function updatestats() {
  var form = this.closest('.statblock-form');
  var obj = form_values(this);
  obj['pk'] = this.querySelector('.statblock').dataset.pk;
  obj['category'] = this.querySelector('.statblock').dataset.category;
  obj['canon'] = this.querySelector('input[type=checkbox]').checked;
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
  var loader = new Loader('statblock');
  let old_sc = get_object_by_id('pcstatblock-' + pk);
  if (old_sc) {
    old_sc.remove();
  }
  post_data("statblock", { pk: pk, category: category }, (data) => {
    loader.remove();
    let div = document.createElement('div');
    div.classList.add('column');

    let statblock = document.getElementById('statblock');
    statblock.insertBefore(div, statblock.firstChild);

    //console.log(data);

    if (data["results"]) {
      //div.classList.add('is-half');
      div.innerHTML = data["results"];
      autojs.rebind();
      add_class_event('generate-image', 'click', imggen);
      add_class_event('statblock-form', 'change', updatestats);
    } else {
      div.innerHTML = "No statblock found";
    }
  });
}

//////////////////////////////////////////  Delete Items  //////////////////////////////////////////

function deleteitem() {
  var item = this.closest('.statcard-item');
  let pk = item.dataset.pk;
  let category = item.dataset.category;
  post_data("delete", { pk: pk, category: category }, (data) => {
    //console.log(data);
    item.remove();
  });
}