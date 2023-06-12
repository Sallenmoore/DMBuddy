//import Sortable from 'sortablejs';
//===My document.ready() handler...
document.addEventListener("DOMContentLoaded", () => {
  //=== Initialize widgets

  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

//===This function handles event binding for anything on the page
//===Bind to existing functions, not anonymous functions

function bindEvents() {

  add_id_event('search-category', 'change', (event) => {
    event.preventDefault();
    document.getElementById("search-category").submit();
  });

  add_id_event('search', 'input', dndfilter);
  add_class_event('referencelist-item', 'click', getstatcard);
  add_id_event('npcgen', 'click', generatenpc);
  add_id_event('encountergen', 'click', generateencounter);
  add_id_event('shopgen', 'click', generateshop);
}

//=== everything below this is all of the other declared functions...

function getstatcard() {
  let pk = this.getAttribute("data-pk");
  let category = get_object_by_id("category");
  post_data("statblock", { pk: pk, category: category.value }, (data) => {
    document.getElementById('reference-detail').innerHTML = data['results'];
  });
}

function dndfilter() {
  let objs = get_objects_by_class("referencelist-item");
  let keyword = this.value;
  if (objs.length > 0) {
    objs.forEach((el) => {
      if (keyword.length <= 2 || el.querySelector("a").innerHTML.toLowerCase().includes(keyword.toLowerCase())) {
        show(el);
      } else {
        hide(el);
      }
    });
  }
}


function generatenpc() {
  post_data("statblock", { pk: "", category: "npc" }, (data) => {
    console.log(data);
    document.getElementById('reference-detail').innerHTML = data[0];
  });
};

function generateencounter() {
  post_data("statblock", { pk: "", category: "encounter" }, (data) => {
    document.getElementById('reference-detail').innerHTML = data[0];
  });
};

function generateshop() {
  post_data("statblock", { pk: "", category: "shop" }, (data) => {
    document.getElementById('reference-detail').innerHTML = data[0];
  });
};
