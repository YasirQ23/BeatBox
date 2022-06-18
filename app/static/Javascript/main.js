const getAuth = async () => {
    const clientID = 'f74d1c3e2d2b4b118fc5462de4b042a3';
    const clientSecret = '685a93cc6572498d98045e4f4c2574ce';
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
}

const loadToken = async () => {
    const token = await getAuth();
    return token
}

const artist_track = {
    'king von': 'took her to the o', 'rauw alejandro': 'fck u x2', 'bad bunny': 'me porto bonito'
    , 'young thug': 'solid', 'jack harlow': 'churchill downs', 'future ': 'purple reign'
    , 'baby keem': 'range brothers', 'lil uzi': '20 min', 'kodak black': 'already'
}

const getData = async () => {
    const token = await loadToken();
    for (let i = 0; i < 9; i++) {
        let data = await fetch(`https://api.spotify.com/v1/search?type=track&q=track:${Object.values(artist_track)[i]}+artist:${Object.keys(artist_track)[i]}&limit=1`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
        data = await data.json();
        image = data.tracks.items[0].album.images[0].url
        imagelocation = document.getElementById(`s-${i}`)
        imagelocation.src = image
        let audio = new Audio(data.tracks.items[0].preview_url)
        let playbutton = document.querySelector(`#s-${i}`)
        playbutton.addEventListener('click', () => audio.play());
        playbutton.addEventListener('dblclick', () => audio.pause());
    }
}




getData()



