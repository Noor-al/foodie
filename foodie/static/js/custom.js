let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['TR']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields

    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({'address' : address}, function(results, status){
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            // console.log('lat=>', latitude)
            // console.log('long=>', longitude)
            $('#id_latitude').val(latitude)
            $('#id_longitude').val(longitude)

            $('#id_address').val(address)

            // var country = results[0].address_components[6].long_name;
            // var state = results[0].address_components[5].long_name;
            // var city = results[0].address_components[5].long_name;
            // var pin_code = results[0].address_components[7].long_name;

            // $('#id_country').val(country)
            // $('#id_state').val(state)
            // $('#id_city').val(city)
            // $('#id_pin_code').val(pin_code)

            console.log(results)
        }
    });

    locDetails = place.address_components
    for(var i=0; i<locDetails.length; i++){
        types = locDetails[i].types
        for(var j=0; j<types.length; j++){
            if(types[j] == 'country')
                $('#id_country').val(locDetails[i].long_name)
            if(types[j] == 'administrative_area_level_1')
                $('#id_state').val(locDetails[i].long_name)
            if(types[j] == 'administrative_area_level_2')
                $('#id_city').val(locDetails[i].long_name)
            if(types[j] == 'postal_code')
                $('#id_pin_code').val(locDetails[i].long_name)
            else 
            $('#id_pin_code').val("")
        }
    }

}
