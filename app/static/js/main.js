
document.addEventListener("DOMContentLoaded", () => {
  //=== Initialize widgets

  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

function bindEvents() {

  add_id_event('search-input', 'input', dndsearch);
  add_id_event('rebuild-db', 'click', rebuilddb);
  add_class_event('statblock', 'click', statcard);
  add_class_event('character-statblock', 'click', characterstatcard);

}

function rebuilddb() {
  let overlay = document.createElement('div');
  overlay.classList.add = "overlay";
  let message = document.createElement('div');
  message.classList.add = "spinner";
  overlay.appendChild(message);
  document.body.appendChild(overlay);
  get_data("updatedb", (data) => {
    console.log(data["results"]);
    overlay.remove();
  });
}

function dndsearch() {
  let keyword = this.value;
  if (keyword.length > 2) {
    var category = get_object_by_id("category").value;
    var results = get_object_by_id("search-results");
    results.innerHTML = "";
    post_data("search", { category: category, keyword: keyword }, (data) => {
      data["results"].forEach((el) => {
        console.log(el);
        results.appendChild(el);
      });
    });
  }
}

function characterstatcard() {
  let pk = this.dataset.pk;
  post_data("statblock", { pk: pk, type: "pc" }, (data) => {
    //console.log(data);
    let results = document.getElementById('detail-view');
    results.innerHTML = "";
    if (data["result"].length > 0) {
      let div = document.createElement('div');
      div.innerHTML = data["result"];
      results.appendChild(div);
    } else {
      results.innerHTML = "No results found";
    }
    add_class_event('inventory-select', 'change', () => {
      get_objects_by_class('item-description').forEach(el => { hide(el); });
      //console.log(this.value);
      show(document.getElementById(this.value));
    });
    add_class_event('spell-select', 'change', () => {
      get_objects_by_class('spell-description').forEach(el => { hide(el); });
      //console.log(this.value);
      show(document.getElementById(this.value));
    });
    add_class_event('monster-select', 'change', () => {
      get_objects_by_class('feature-description').forEach(el => { hide(el); });
      //console.log(this.value);
      show(document.getElementById(this.value));
    });
  });
}


function statcard() {
  var pk = this.getAttribute("data-pk");
  var category = this.getAttribute("data-category");
  fetch("statblock", {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    mode: "same-origin", // no-cors, *cors, same-origin
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ pk: pk, category: category.value }), // body data type must match "Content-Type" header
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      let ref_detail = document.getElementById('reference-detail');
      ref_detail.innerHTML = data['results'];
    })
    .then(() => {

      if (category.value == "items") {
        console.log(category.value);
        add_class_event('item-details', 'input', updateitem);
      } else if (category.value == "monsters") {
        add_class_event('monster-details', 'input', updatemonster);
      } else if (category.value == "spells") {
        add_class_event('spell-details', 'input', updatespell);
      } else if (category.value == "npcs") {
        add_class_event('npc-details', 'input', updatenpc);
      } else if (category.value == "shops") {
        add_class_event('shop-details', 'input', updateshop);
      } else {
        console.log("no category");
      }
    })
    .catch((error) => {
      console.log(error);
    });
}

