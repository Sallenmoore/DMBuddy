//import Sortable from 'sortablejs';
//===My document.ready() handler...
document.addEventListener("DOMContentLoaded", () => {
  //=== Initialize widgets
  let initiative = document.getElementById('battle-initiative');
  if (initiative) {
    var sortable = Sortable.create(initiative);
  }
  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

//===This function handles event binding for anything on the page
//===Bind to existing functions, not anonymous functions

function bindEvents() {

  add_id_event('search', 'change', dndsearch);
  add_id_event('pc_add', 'click', pcadd);
  add_id_event('remove-from-initiative', 'click', removefrominitiative);
  add_id_event('initiative-form', 'click', addtoinitiative);
  add_event(document.getElementById('pc-list').childNodes, 'click', detailview);
  add_id_event('update-pcs', 'click', updatepcs);
  add_id_event('showdmnotes', 'click', showdmnotes);

}

//===Then everything below this is all of the other declared functions...

function showdmnotes() {
  let dmnotes = document.getElementById('dmnotes');
  if (dmnotes.classList.contains('is-active')) {
    dmnotes.classList.remove('is-active');
  } else {
    dmnotes.classList.add('is-active');
  }
}

function updatepcs() {
  get_data("updatepcs");
}

function showitemdescription() {
  get_objects_by_class('item-description').forEach(el => { hide(el); });
  //console.log(this.value);
  show(document.getElementById(this.value));
}

function showspelldescription() {
  get_objects_by_class('spell-description').forEach(el => { hide(el); });
  //console.log(this.value);
  show(document.getElementById(this.value));
}

function showfeaturedescription() {
  get_objects_by_class('feature-description').forEach(el => { hide(el); });
  //console.log(this.value);
  show(document.getElementById(this.value));
}

function detailview() {
  let pk = this.dataset.pk;
  post_data("getstatblock", { pk: pk }, (data) => {
    console.log(data);
    let results = document.getElementById('detail-view');
    results.innerHTML = "";
    if (data["result"].length > 0) {
      let div = document.createElement('div');
      div.innerHTML = data["result"];
      results.appendChild(div);
    } else {
      results.innerHTML = "No results found";
    }
    add_class_event('inventory-select', 'change', showitemdescription);
    add_class_event('spell-select', 'change', showspelldescription);
    add_class_event('feature-select', 'change', showfeaturedescription);
  });
}

function dndsearch() {
  if (this.value.length > 2) {
    let cat = document.getElementById('category').value;
    console.log(cat);
    let keyword = this.value;
    post_data("search", { keyword: keyword, category: cat }, (data) => {
      console.log(data);
      let results = document.getElementById('results');
      results.innerHTML = "";
      if (data.length > 0) {
        data.forEach((item) => {
          let div = document.createElement('div');
          div.classList.add('column');
          div.innerHTML = item;
          results.appendChild(div);
        });
      } else {
        let li = document.createElement('li');
        li.innerHTML = "No results found";
        results.appendChild(li);
      }
    });
  }
}

function pcadd() {
  let pc = document.getElementById('pc_id').value;
  post_data("getplayer", { pc: pc }, (data) => {
    console.log(data);
    let li = document.createElement('li');
    li.innerHTML = data.name;
    let pc_list = document.getElementById('pc_list');
    pc_list.appendChild(li);
    document.getElementById('pc_id').value = "";
  });
}

function removefrominitiative() {
  let li = this.closest("li");
  let pk = li.dataset.pk;
  li.parentNode.removeChild(li);
  post_data("toggleinitiative", { pk: pk }, (data) => {
    console.log(data);
  });
}

function addtoinitiative() {
  let li = this.closest("li");
  let pk = li.dataset.pk;
  post_data("toggleinitiative", { pk: pk }, (data) => {
    let initiative_li = document.createElement('li');
    initiative_li.innerHTML = `
      <div class="media">
          <div class="media__left">
              <div class="image round is-thumbnail is-tiny">
                  <img src="${data.image}">
              </div>
          </div>
          <div class="media__content">
              <p>${data.name}</p>
          </div>
          <div class="media__right">
              <a class="button is-small circle" id="remove-from-initiative">
                  <iconify-icon icon="mdi:remove"></iconify-icon>
              </a>
          </div>
      </div>
    `;
    document.getElementById("battle-initiative").append(initiative_li);
  });
}