

// Fires before Safari navigates to a new page
safari.application.addEventListener('beforeNavigate', handleEvent, true);

// Logs the event and the url
function handleEvent(event) {
    console.log(event);
    console.log(event.url);
}
