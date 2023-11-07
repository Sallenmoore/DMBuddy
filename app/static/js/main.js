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

  // Reference
  //add_id_event('search-input', 'input', dndsearch);
  //add_id_event('category', 'change', dndsearch);

  // NPC
  add_class_event('npc-list', 'change', pcstatcard);
  add_id_event('generate-npc', 'click', npcgen);
  add_id_event('update-canon-npc', 'click', update_canon_npc);
  add_id_event('chat-form', 'submit', npcchat);
}

/////////////////////////////////////// TASK Functions //////////////////////////////////////////

function getTaskStatus(taskID, f = () => console.log("Task Ended")) {
  post_data("checktask", { "id": taskID }, res => {
    console.log(res);
    if (res.status != 'finished' && res.status != 'failed') {
      setTimeout(() => { getTaskStatus(taskID, f); }, 3000);
    } else {
      console.log("Task results: " + res.results);
      f();
    }
  });
}

function npcgen() {
  get_data("npcgen", (data) => {
    //console.log(data);
    getTaskStatus(data.results);
  });
}

function imggen() {
  let statblock = this.closest('.statblock');
  let pk = statblock.dataset.pk;
  let category = statblock.dataset.category;
  //loader.show('npc-image-portrait');
  post_data("imagegen", { "pk": pk, "category": category }, (data) => {
    getTaskStatus(data.results, () => {
      //loader.remove();
      statcard(pk, category);
    });
  });
}

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

////////////////////////////////////// CRUD Calls //////////////////////////////////////////

///////////////// READ ////////////////////////

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

///////////////// Statcards ////////////////////////
function pcstatcard() {
  var pk = this.value;
  var category = this.dataset.category;
  statcard(pk, category);
}

function statcard(pk, category) {
  get_object_by_id('statblock').innerHTML = "";
  loader.show('statblock');
  if (pk && category) {
    post_data("statblock", { pk: pk, category: category }, (data) => {
      loader.remove();
      let div = document.createElement('div');
      div.classList.add('column');
      let statblock = document.getElementById('statblock');
      statblock.append(div);
      //console.log(data);

      if (data["results"]) {
        //div.classList.add('is-half');
        div.innerHTML = data.results.statblock;

        add_class_event('generate-npc-image', 'click', imggen);
        add_class_event('autocomplete-profile', 'click', autocompleteprofile);
        add_class_event('save-updates', 'click', updatestats);
        add_class_event('npc-connections-list', 'change', updateconnection);
        add_class_event('delete-npc', 'click', deletenpc);
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

  } else {
    loader.remove();
  }
}

//////////////// UPDATE //////////////////////

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
    statcard(obj['pk'], obj['category']);
    if (data.results.canon) {
      //TBD
      console.log("TODO: Move to Canon");
    }
  });
}

function autocompleteprofile() {
  let data = { pk: this.closest('.statblock').dataset.pk };
  loader.show(this.closest('.statblock').id);
  post_data("npcgen", data, (data) => {
    loader.remove();
    statcard(data['pk'], "NPC");
  });
}

function updateconnection() {
  var conn_pk = this.value;
  hide(get_objects_by_class('npc-connection'));
  let pk = this.closest('.statcard').dataset.pk;
  get_object_by_id('#npc-connection-' + pk + '-' + conn_pk).dataset.pk;
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

//////////////// DELETE //////////////////////
function deletenpc() {
  var item = this.closest('.statblock');
  let pk = item.dataset.pk;
  let category = item.dataset.category;
  post_data("npc-delete", { pk: pk, category: category }, (data) => {
    //console.log(data);
    item.remove();
  });
}
