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

  add_selector_event('#nav_links a', 'click', navlinks);

  add_id_event('search', 'input', dndsearch);

  //add_id_event('remove-from-initiative', 'click', removefrominitiative);
  //add_event(document.getElementById('pc-list').childNodes, 'click', detailview);

  //add_id_event('pc_add', 'click', pcadd);
  //add_id_event('update-pcs', 'click', updatepcs);
  //add_id_event('initiative-form', 'click', addtoinitiative);


  add_id_event('map-file', 'change', mapupload);
  add_id_event('map-reset', 'click', mapreset);
  add_id_event('map-grid', 'click', mapgrid);
  add_class_event('map-entry', 'click', displaymap);
}

//=== everything below this is all of the other declared functions...

function navlinks() {
  get_objects_by_class('dmpanel').forEach(el => { hide(el); });
  get_objects_by_class('dmdetail').forEach(el => { hide(el); });
  let target = get_object_by_id(this.dataset.target + "-panel");
  let detail = get_object_by_id(this.dataset.target + "-detail");
  show(target);
  show(detail);
}

//#########################################################
//#  Maps
//#########################################################

function mapreset() {
  get_data("mapentries", (data) => {
    var backgroundImage = document.getElementById('map-image');
    backgroundImage.style.left = 0;
    backgroundImage.style.top = 0;
    backgroundImage.style.transform = `scale(1)`;
  });
}

function mapgrid() {
}

function mapentries() {
  get_data("mapentries", (data) => {
    document.getElementById('map-list').innerHTML = "";
    console.log(data.results);
    data.results.forEach((entry) => {
      let elem = document.createRange().createContextualFragment(entry);
      document.getElementById('map-list').appendChild(elem);
    });
    add_class_event('map-entry', 'click', displaymap);
  });
}

function mapupload() {
  //console.log(this.files[0]);
  let file = this.files[0];
  let data = new FormData();
  data.append('file', file);
  fetch("mapupload", {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    mode: "same-origin", // no-cors, *cors, same-origin
    body: data, // body data type must match "Content-Type" header
  })
    .then((res) => {
      return mapentries();
    })
    .catch((error) => {
      console.log(error);
    });
}

function displaymap() {
  var map_image = this.querySelector('img').src;
  var imageContainer = document.getElementById('map-container');
  var backgroundImage = document.getElementById('map-image');
  backgroundImage.src = map_image;
  document.getElementById('map-zoom').value = 1;
  var isDragging = false;

  var scrollX = 0;
  var scrollY = 0;

  var zoomScale = 0;

  backgroundImage.addEventListener('mousedown', (e) => {
    console.log('mousedown');
    isDragging = true;
    backgroundImage.style.cursor = 'grabbing';
    //backgroundImage.style.pointerEvents = 'none';
  });

  backgroundImage.addEventListener('mousemove', (e) => {
    console.log('mousemove');
    if (!isDragging) return;
    // let posX = e.clientX - startScrollX;
    // let posY = e.clientY - startScrollY;
    scrollX += e.movementX;
    scrollY += e.movementY;
    //console.log(e.clientX, e.layerX, e.movementX, e.offsetX, e.pageX, e.screenX, e.x);
    //backgroundImage.style.transform = `translate(${posX}px, ${posY}px) scale(${zoomScale})`;
    backgroundImage.style.left = `${scrollX}px`;
    backgroundImage.style.top = `${scrollY}px`;

  });

  backgroundImage.addEventListener('mouseup', (e) => {
    isDragging = false;
    backgroundImage.style.cursor = 'move';
  });

  document.getElementById('map-zoom').addEventListener("input", (e) => {
    console.log(e.target.value); // 'e' is the event object
    zoomScale = 1 + (e.target.value * 5) * 0.01;
    //backgroundImage.style.transform = `translate(${posX}px, ${posY}px) scale(${zoomScale})`;
    backgroundImage.style.transform = `scale(${zoomScale})`;
  });
}


//#########################################################
//#  Players
//#########################################################
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
    add_class_event('inventory-select', 'change', showitemdescription);
    add_class_event('spell-select', 'change', showspelldescription);
    add_class_event('monster-select', 'change', showfeaturedescription);
  });
}

//#########################################################
//#  Reference
//#########################################################
function dndsearch() {
  if (this.value.length > 2) {
    let cat = document.getElementById('category').value;
    //console.log(cat);
    let keyword = this.value;
    post_data("search", { keyword: keyword, category: cat }, (data) => {
      //console.log(data);
      let results = document.getElementById('reference-detail');
      results.innerHTML = "";
      let row = document.createElement('div');
      row.classList.add('row');
      if (data.length > 0) {
        data.forEach((item) => {
          let column = document.createElement('div');
          column.classList.add('column');
          column.classList.add('is-full');
          column.innerHTML = item;
          row.appendChild(column);
        });
        results.appendChild(row);
        add_class_event('add-mob-initiative', 'click', addmobinitiative);
      } else {
        results.innerHTML = "<h2>No results found</h2>";
      }
    });
  }
}


//#########################################################
//#  initiative
//#########################################################
function addmobinitiative() {
  let mc = this.closest(".mobcard");
  let pk = mc.dataset.pk;
  post_data("addtoinitiative", { pk: pk, type: "monster" }, (data) => {
    document.getElementById('initiative-available').innerHTML = data["results"];
  });
};

function addpctoinitiative() {
  let li = this.closest("li");
  let pk = li.dataset.pk;
  post_data("addtoinitiative", { pk: pk, type: "player" }, (data) => {
    document.getElementById('initiative-available').innerHTML = data["results"];
  });
}

// function pcadd() {
//   let pc = document.getElementById('pc_id').value;
//   post_data("getplayer", { pc: pc }, (data) => {
//     console.log(data);
//     let li = document.createElement('li');
//     li.innerHTML = data.name;
//     let pc_list = document.getElementById('pc_list');
//     pc_list.appendChild(li);
//     document.getElementById('pc_id').value = "";
//   });
// }

// function removefrominitiative() {
//   let li = this.closest("li");
//   let pk = li.dataset.pk;
//   li.parentNode.removeChild(li);
//   post_data("toggleinitiative", { pk: pk }, (data) => {
//     console.log(data);
//   });
// }

// function insertinitiative(data) {
//   let initiative_li = document.createElement('li');
//   initiative_li.innerHTML = `
//     <div class="media">
//         <div class="media__left">
//             <div class="image round is-thumbnail is-tiny">
//                 <img src="${data.image}">
//             </div>
//         </div>
//         <div class="media__content">
//             <p>${data.name}</p>
//         </div>
//         <div class="media__right">
//             <a class="button is-small circle" id="remove-from-initiative">
//                 <iconify-icon icon="mdi:remove"></iconify-icon>
//             </a>
//         </div>
//     </div>
//   `;
//   document.getElementById("battle-initiative").append(initiative_li);
// }



