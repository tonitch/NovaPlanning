const ics_events = [];

async function fetch_events(){

    // return  fetch('events.json').then((response) => response.json())
    return  fetch('https://raw.githubusercontent.com/tonitch/NovaPlanning/refs/heads/action/events.json').then((response) => response.json())
}
