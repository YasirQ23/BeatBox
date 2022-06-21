const getAuth = async () => {
    const clientID = '35368c1ad4624a369969e2d70b417fee';
    const clientSecret = '6ecad3bc2e2546869f62d7ee68f74e1b';
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
    for (let i = 0; i < artists_tracks.length; i += 2) {
        let data = await fetch(`https://api.spotify.com/v1/search?type=track&q=track:${artists_tracks[i + 1]}+artist:${artists_tracks[i]}&limit=1`,
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
                currently.innerHTML = `Playing: ${artists_tracks[x * 2]} - ${artists_tracks[(x * 2) + 1]}`
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
    currently.innerHTML = `Playing: ${artists_tracks[x * 2]} - ${artists_tracks[(x * 2) + 1]}`
    currently.hidden = false;
};

let stopSong = () => {
    playing.pause();
    stopbtn.disabled = true;
    currently.hidden = true;
};

