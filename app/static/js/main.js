document.addEventListener("DOMContentLoaded", () => {
  //=== configure autojs
  autojs.configure();
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

  add_id_event('chat-form', 'submit', npcchat);

  // Element Tester
  //var loader = new Loader('tester');
}

/////////////////////////////////////// Chat Functions //////////////////////////////////////////

function npcchat(e) {
  e.preventDefault();
  var message = get_object_by_id('pc-chat').value;
  var pk = get_object_by_id('chat-form').dataset.pk;
  var loader = new Loader('chat-form');
  post_data("npcchat", { "pk": pk, "message": message }, (data) => {
    loader.remove();
    var npcchat = document.createElement('div');
    npcchat.classList.add('column');

    var response = document.createElement('div');
    response.innerHTML = data.results;
    response.classList.add('chat-message', "panel", "has-bg-dark");
    npcchat.appendChild(response);
    prepend_to_id('npc-chat', npcchat);
  });
}

/////////////////////////////////////// TASK Functions //////////////////////////////////////////

function getTaskStatus(taskID, iters) {
  var loader = new Loader();
  post_data("checktask", { "id": taskID }, res => {
    // console.log(res);
    // console.log(res.results.task_id);
    // console.log(res.results.task_status);
    // console.log(res.results.task_results);
    // console.log(iters);
    if (iters > 0 && res.results.task_status != 'SUCCESS' && res.results.task_status != 'FAILURE') {
      setTimeout(() => getTaskStatus(taskID, iters - 1), 3000);
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
    var loader = new Loader("search-results");
    post_data("search", { category: category, keyword: keyword }, (data) => {
      results.innerHTML = "";
      loader.remove();
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
  var loader = new Loader("npc-tab");
  get_data("canonupdates", (data) => {
    loader.remove();
    for (let i = 0; i < data.results.length; i++) {
      let el = data.results[i];

      var li = get_object_by_id("search-result-item-template").cloneNode(true);
      li.querySelector('a').innerHTML = el["name"];
      get_object_by_id('canon-npc-list').appendChild(li);
    }
  });
}

function updatestats() {
  var form = this.closest('.statblock-form');
  var obj = form_values(form);
  obj['pk'] = form.querySelector('.statblock').dataset.pk;
  obj['category'] = form.querySelector('.statblock').dataset.category;
  obj['canon'] = form.querySelector('input[type=checkbox]').checked;
  console.log(obj);
  var loader = new Loader(form.querySelector('.statblock').id);
  post_data("npc-updates", obj, (data) => {
    loader.remove();
    console.log(data);
    var li = get_object_by_id("list-npc-" + data.results.pk);
    console.log(li);
    if (!li) {
      li = create_list_item(data.results.pk, data.results.category);
      if (data.results.canon) {
        get_object_by_id('canon-npc-list').appendChild(li);
      } else {
        get_object_by_id('free-npc-list').appendChild(li);
      }
    } else {
      if (data.results.canon) {
        get_object_by_id('canon-npc-list').appendChild(li);
      } else {
        get_object_by_id('free-npc-list').appendChild(li);
      }
    }
  });
}

function updateconnection() {
  var conn_pk = this.value;
  hide(get_objects_by_class('npc-connection'));
  let pk = this.closest('.statcard').dataset.pk;
  get_object_by_id('#npc-connection-' + pk + '-' + conn_pk).dataset.pk;
}

function statcard() {
  var item = this.closest('.statcard-item');
  let pk = item.dataset.pk;
  let category = item.dataset.category;
  var name = item.querySelector('.statcard-view').innerHTML;
  let old_sc = get_object_by_id('pcstatblock-' + pk);
  if (old_sc) {
    old_sc.remove();
  }
  var loader = new Loader('statblock');
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
      add_class_event('generate-image', 'click', imggen);
      add_class_event('save-updates', 'click', updatestats);
      add_class_event('npc-connections-list', 'change', updateconnection);
      get_object_by_id("chat-form").dataset.pk = pk;
      get_object_by_id("chat-name").innerHTML = name;
      autojs.rebind();
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
  post_data("npc-delete", { pk: pk, category: category }, (data) => {
    //console.log(data);
    item.remove();
  });
}

//////////////////////////////////////////  Utilities  //////////////////////////////////////////

function create_list_item(pk, category) {
  var li = get_object_by_id("search-result-item-template").cloneNode(true);
  li.dataset.pk = pk;
  li.dataset.category = category;
  li.id = "list-" + category.toLowerCase() + "-" + pk;
  return li;
}