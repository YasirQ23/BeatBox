const getAuth = async () => {
    const clientID = '35368c1ad4624a369969e2d70b417fee';
    const clientSecret = secret_ ;
    const encodedString = btoa(clientID + ':' + clientSecret);
    const response = await fetch('https://accounts.spotify.com/api/token',
        {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${encodedString}`,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'grant_type=client_credentials'
        }
    );
    let token = await response.json();
    return token.access_token
};

const loadToken = async () => {
    const token = await getAuth();
    return token
};

const getData = async (x, y) => {
    const token = await loadToken();
    let data = await fetch(`https://api.spotify.com/v1/search?type=track&q=track:${y}+artist:${x}&limit=1`,
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
    data = await data.json();
    music = data
    if (data.tracks.items.length == 0) {
        selectorgrid.hidden = true;
        imagelocation = document.getElementById(`s-1`)
        imagelocation.src = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png'
        currently.innerHTML = `Sorry, but nothing matched that artist and track name. Please try again with a different artist or track!`
        currently.hidden = false;
        stopbtn.hidden = true;
    } else {
        createTile(data);
    }
};

orignaltext = document.getElementById(`s-1`).onclick;

const createTile = (data) => {
    originalText = document.getElementById('s-1').onclick
    if (music.tracks.items[0].preview_url == null) {
        imagelocation = document.getElementById(`s-1`)
        imagelocation.src = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png'
        currently.innerHTML = `${music.tracks.items[0].artists[0].name} - ${music.tracks.items[0].name} is unavailable due to copyright restrictions`
        currently.hidden = false;
        selectorgrid.hidden = true;
        document.getElementById(`s-1`).onclick = ''
        stopbtn.hidden = true;
    } else {
        try {
            image = data.tracks.items[0].album.images[0].url
            imagelocation = document.getElementById(`s-1`)
            imagelocation.src = image
            document.getElementById(`s-1`).onclick = orignaltext
            saveSongDB();
        }
        catch (err) {
            imagelocation = document.getElementById(`s-1`)
            imagelocation.src = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png'
            currently.innerHTML = `${music.tracks.items[0].artists[0].name} - ${music.tracks.items[0].name} is unavailable due to copyright restrictions`
            currently.hidden = false;
            selectorgrid.hidden = true;
            document.getElementById(`s-1`).onclick = ''
            stopbtn.hidden = true;
        }
    }
};

let form = document.getElementById('infoform');
let button3 = document.getElementById('submit-btn')

button3.addEventListener('touchend', (event) => {
    event.preventDefault();
    let x = document.getElementById("artist").value;
    let y = document.getElementById("track").value;
    form.reset();
    data = getData(x, y);
    stopbtn.hidden = false;
    addbtn.hidden = false;
    selectorgrid.hidden = false;
    currently.hidden = false;
    stopSong();
});

form.addEventListener('submit', (event) => {
    event.preventDefault();
    let x = event.path[0][0].value;
    let y = event.path[0][1].value;
    form.reset();
    data = getData(x, y);
    stopbtn.hidden = false;
    addbtn.hidden = false;
    selectorgrid.hidden = false;
    currently.hidden = false;
    stopSong();
});

let music;
let playing;
let stopbtn = document.getElementById('stopbtn');
let currently = document.getElementById('currently');

let clickEvent = () => {
    let clicked = music.tracks.items[0].preview_url;

    if (playing) {
        if (clicked == playing.src) {
            if (playing.paused) {
                playing.play();
                currently.innerHTML = `Playing: ${music.tracks.items[0].artists[0].name} - ${music.tracks.items[0].name}`
                currently.hidden = false;
                return
            } else {
                stopSong();
                return
            }
        } else if (!playing.paused) {
            stopSong();
        }
    }
    playing = new Audio(clicked);

    playing.play();
    currently.innerHTML = `Playing: ${music.tracks.items[0].artists[0].name} - ${music.tracks.items[0].name}`
    currently.hidden = false;
};


let stopSong = () => {
    playing.pause();
    currently.hidden = true;
};

let saveSongDB = () => {
    document.getElementById("grid_artist").value = music.tracks.items[0].artists[0].name;
    document.getElementById("grid_track").value = music.tracks.items[0].name;
    document.getElementById("grid_img").value = music.tracks.items[0].album.images[0].url;
};

let gridSelection = (input) => {
    document.getElementById("grid_location").value = input
    document.getElementById("grid-btn").click()
};



