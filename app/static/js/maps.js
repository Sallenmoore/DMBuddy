//import Sortable from 'sortablejs';
//===My document.ready() handler...
document.addEventListener("DOMContentLoaded", () => {
  //--Set up events
  bindEvents();
});

//===This function handles event binding for anything on the page
//===Bind to existing functions, not anonymous functions

function bindEvents() {

  document.getElementById('map-image').ondragstart = function () { return false; };

  add_id_event('add-map-form', 'change', (event) => {
    event.preventDefault();
    document.getElementById("add-map-form").submit();
  });
  add_id_event('map-grid', 'click', (event) => {
    mapgrid();
    toggle(document.getElementById('map-grid-overlay'));
  });

  add_id_event('map-gridsize', 'change', mapgrid);
  add_id_event('map-reset-fog', 'click', mapgrid);
  add_id_event('map-clear-fog', 'click', mapclearfog);
  add_id_event('map-list', 'change', displaymap);
}

//=== everything below this is all of the other declared functions...


//#########################################################
//#  functions
//#########################################################

var map_fog_list = [];

function mapclearfog() {
  let objs = get_objects_by_class('grid-cell');
  if (objs.length > 0) {
    objs.forEach((el) => {
      el.classList.remove('fog-grid');
      el.classList.add('clear-grid');
    });
  }
}

function mapgrid() {
  var gridOverlay = document.getElementById('map-grid-overlay');
  // Get the target element by its ID
  let image = document.getElementById('map-image');
  let container = document.getElementById('map-container');
  container.style.width = gridOverlay.style.width = image.scrollWidth + 'px';
  container.style.height = gridOverlay.style.height = image.scrollHeight + 'px';
  let grid_size = document.getElementById('map-gridsize').value;
  let numHorizontalLines = Math.ceil(image.scrollHeight / grid_size);
  let numVerticalLines = Math.ceil(image.scrollWidth / grid_size);

  map_fog_list = [...Array(numVerticalLines)].map(() => Array(numHorizontalLines).fill('fog-grid'));

  gridOverlay.innerHTML = '';
  for (let i = 0; i < numVerticalLines; i++) {
    for (let j = 0; j < numHorizontalLines; j++) {
      let gridcell = document.createElement('div');
      gridcell.classList.add(map_fog_list[i][j], 'grid-cell');
      gridcell.style.top = j * grid_size + 'px';
      gridcell.style.left = i * grid_size + 'px';
      gridcell.style.height = gridcell.style.width = grid_size + 'px';

      gridcell.addEventListener('mousemove', (event) => {
        if (event.buttons == 1) {
          event.target.classList.remove('fog-grid');
          event.target.classList.add('clear-grid');
        }
      });
      gridOverlay.appendChild(gridcell);
    }
  }
}


function displaymap() {
  document.getElementById('map-image').src = document.getElementById("map-list").value;
  //hide(document.getElementById('map-grid-overlay'));
}
