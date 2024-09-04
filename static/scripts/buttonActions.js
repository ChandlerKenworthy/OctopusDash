document.getElementById("fetchDataButton").addEventListener("click", function() {
    fetch('/get_more_data', {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            alert('Data fetched successfully!');
            window.location.reload();  // Reload the page to see the updated data
        } else {
            alert('Failed to fetch data.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById("fetchUsageButton").addEventListener("click", function() {
    fetch('/get_usage_data', {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            alert('Data fetched successfully!');
            window.location.reload();  // Reload the page to see the updated data
        } else {
            alert('Failed to fetch data.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
});
