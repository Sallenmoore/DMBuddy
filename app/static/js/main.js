var loader = new Loader('statblock');

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
  loader.show('chat-form');
  post_data("npcchat", { "pk": pk, "message": message }, (task) => {
    get_object_by_id("pc-chat").value = "";
    getTaskStatus(task.results,
      () => {
        post_data("npc", { "pk": pk }, (res) => {

          loader.remove();
          console.log(res);
          get_object_by_id("npcchat-message").innerHTML = res.results.conversation_summary.message;

          get_object_by_id("npcchat-response").innerHTML = res.results.conversation_summary.response;

          get_object_by_id("npcchat-summary").innerHTML = res.results.conversation_summary.summary;
        });
      });
  });
}

/////////////////////////////////////// TASK Functions //////////////////////////////////////////

function getTaskStatus(taskID, f = () => { }) {
  post_data("checktask", { "id": taskID }, res => {
    console.log(res);
    if (res.results != 'finished' && res.results != 'failed') {
      setTimeout(() => {
        getTaskStatus(taskID, f);
      }, 3000);
    } else {
      //console.log(f);
      f();
    }

  });
}

function task(task_name, task_data = {}) {
  post_data(task_name, task_data, (data) => {
    //console.log(data);
    setTimeout(() => getTaskStatus(data.results), 100);
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
    loader.show("search-results");
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
  loader.show("npc-tab");
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
  loader.show(form.querySelector('.statblock').id);
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
  loader.show('statblock');
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
      var npcchat = get_object_by_id("npcchat-message");
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