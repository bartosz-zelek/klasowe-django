function change_year(){
    year = document.querySelector('#year').value;
    console.log(year)
    location.search = '?year='+year;
}