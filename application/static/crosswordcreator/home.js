$(document).ready(function () {
    playerIdCookie();
});

function playerIdCookie() {
    if (!document.cookie.split('; ').find(row => row.startsWith('playerId'))) {
        const playerId = createUUID();
        console.info(`Set player ID to: ${playerId}`);
        document.cookie = `playerId=${playerId}; max-age=7890000`;
    } else {
        console.info(`Detected player ID: ${getPlayerId()}`)
    }

    document.getElementById("player_id_create").setAttribute("value", getPlayerId());
    document.getElementById("player_id_join").setAttribute("value", getPlayerId());
}

function getPlayerId() {
    return document.cookie.split('; ').find(row => row.startsWith('playerId')).split('=')[1];
}

function createUUID() {
    return 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'.replace(/x/g, function (_) {
        return Math.floor(Math.random() * 16).toString(16);
    });
}
