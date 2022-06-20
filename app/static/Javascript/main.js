const getAuth = async () => {
    const clientID = '';
    const clientSecret = '';
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

const getData = async () => {
    const token = await loadToken();
    for (let i = 0; i < myVar.length; i += 2) {
        let data = await fetch(`https://api.spotify.com/v1/search?type=track&q=track:${myVar[i + 1]}+artist:${myVar[i]}&limit=1`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
        data = await data.json();
        music.push(data.tracks.items[0].preview_url)
    }
};

let music = []
let playing;
let stopbtn = document.getElementById('stopbtn');
let currently = document.getElementById('currently');

getData();

let clickEvent = (x) => {
    let clicked = music[x]

    if (playing) {
        if (clicked == playing.src) {
            if (playing.paused) {
                playing.play();
                currently.innerHTML = `Playing: ${myVar[x * 2]} - ${myVar[(x * 2) + 1]}`
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
    stopbtn.disabled = false;
    currently.innerHTML = `Playing: ${myVar[x * 2]} - ${myVar[(x * 2) + 1]}`
    currently.hidden = false;
};


let stopSong = () => {
    playing.pause();
    stopbtn.disabled = true;
    currently.hidden = true;
};

