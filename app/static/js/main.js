//===My document.ready() handler...
document.addEventListener("DOMContentLoaded", () => {
  //=== Initialize widgets
  const gridItems = document.querySelectorAll('.grid > .cell.dungeon-cell');
  const width = gridItems[0].clientWidth;
  gridItems.forEach(item => {
    item.style.height = `${width}px`;
  });
  //=== do some code stuff...

  //--Set up events
  bindEvents();
});

//===This function handles event binding for anything on the page
//===Bind to existing functions, not anonymous functions

function bindEvents() {

  document.getElementById('search').addEventListener('change', dndsearch);

}

//===Then everything below this is all of the other declared functions...

function dndsearch() {
  if (this.value.length > 2) {
    let cat = document.getElementById('category').value
    getJsonFromApi("https://api.open5e.com", cat, this.value, (data) => { 
      console.log(data);
      results = {}
      for (o in data.results) {
        results = {name:o.name, type:o.subtype, slug:o.slug}
      }
      document.getElementById('results').innerHTML = JSON.stringify(results);
    });
  }
}
