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
  var npcchat = get_object_by_id("npcchat-message");
  post_data("npcchat", { "pk": pk, "message": message }, (task) => {
    setTimeout(() => {
      getTaskStatus(task.results, (res) => {
        get_object_by_id("pc-chat").value = "";
        npcchat.innerHTML = res.results.task_results.message;
        var npcresponse = get_object_by_id("npcchat-response");
        npcresponse.innerHTML = res.results.task_results.response;
        var npcchat_summary = get_object_by_id("npcchat-summary");
        npcchat_summary.innerHTML = res.results.task_results.summary;
        loader.remove();
      });
    }, 3000);
  });
}

/////////////////////////////////////// TASK Functions //////////////////////////////////////////

function getTaskStatus(taskID, f = () => { console.log("Task Complete"); }) {
  post_data("checktask", { "id": taskID }, res => {
    // console.log(res);
    // console.log(res.results.task_id);
    // console.log(res.results.task_status);
    // console.log(res.results.task_results);
    // console.log(iters);
    if (res.results.task_status != 'SUCCESS' && res.results.task_status != 'FAILURE') {
      setTimeout(() => {
        getTaskStatus(taskID);
      }, 3000);
    } else {
      f(res.results.task_results);
    }

  });
}

function task(task_name, loader, task_data = {}) {
  post_data(task_name, task_data, (data) => {
    //console.log(data);
    setTimeout(() => getTaskStatus(data.results, (loader) => { loader.remove(); }), 100);
  });
}

function npcgen() {
  var loader = new Loader('statblock');
  task("npcgen", loader);
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
      div.innerHTML = data.results.statblock;
      add_class_event('generate-image', 'click', imggen);
      add_class_event('save-updates', 'click', updatestats);
      add_class_event('npc-connections-list', 'change', updateconnection);
      get_object_by_id("chat-form").dataset.pk = data.results.obj.pk;
      get_object_by_id("chat-name").innerHTML = data.results.obj.name;
      get_object_by_id("pc-chat").value = "";
      npcchat.innerHTML = data.results.obj.conversation_summary.message;
      var npcresponse = get_object_by_id("npcchat-response");
      npcresponse.innerHTML = data.results.obj.conversation_summary.response;
      var npcchat_summary = get_object_by_id("npcchat-summary");
      npcchat_summary.innerHTML = data.results.obj.conversation_summary.summary;
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