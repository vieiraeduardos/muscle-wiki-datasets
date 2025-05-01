// Select all checkboxes and mark them as checked
await document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.checked = true;
});

// Function to save JSON as a file
function save_json(data, file_name) {
    // Convert the object to a JSON string
    const json_string = JSON.stringify(data, null, 2);

    // Create a blob with the JSON content
    const blob = new Blob([json_string], { type: "application/json" });

    // Create a link for download
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = file_name;

    // Simulate a click on the link to start the download
    link.click();

    // Release the object URL
    URL.revokeObjectURL(url);
}

// Function to clean the equipment text
function clean_equipment(text) {
    // Remove CSS and get only the part after the last "}"
    return text.split("}").pop().trim();
}

// Select all table rows
let rows = document.querySelectorAll("tr");

// Array to store table data
let table_data = [];

let category = "";

// Iterate over each row
rows.forEach(row => {
    // Check if the row contains <th> (header)
    let header = row.querySelector("th");
    if (header) {
        category = header.textContent.trim();
    } else {
        // If it's a normal row, process the <td> columns
        let columns = row.querySelectorAll("td");

        // Check if the row has at least 4 columns
        if (columns.length >= 4) {
            // 1st TD: Get the text from the <a> tag (if it exists)
            let exercise = columns[0].querySelector("a")?.textContent.trim() || "N/A";

            // 2nd TD: Get the href from all <a> tags (if they exist)
            let video_links = [];
            columns[1].querySelectorAll("a").forEach(link => {
                video_links.push(link.href || "N/A");
            });

            // 3rd TD: Get the text from the <span> tag (if it exists) and clean the CSS
            let equipment = columns[2].querySelector("span")?.textContent.trim() || "N/A";
            equipment = clean_equipment(equipment); // Apply the cleaning function

            // 4th TD: Get the text from the <span> tag (if it exists)
            let difficulty = columns[3].querySelector("span")?.textContent.trim() || "N/A";

            // Add the row data to the array
            table_data.push({
                category: category, // Empty header for normal rows
                exercise: exercise,
                male_url: video_links[0] || "N/A",
                female_url: video_links[1] || "N/A",
                equipment: equipment,
                difficulty: difficulty
            });
        } else {
            console.log("Row ignored: does not have 4 columns.");
        }
    }
});

// Save the data to a JSON file
save_json(table_data, "table_data.json");

// Execute the main function
main();