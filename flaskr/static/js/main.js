document.addEventListener("DOMContentLoaded", function () {
    // ================== Search Elements ==================
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const fieldSelect = document.getElementById('search-field');
    const searchButton = document.getElementById('search-button');
    const resultsTableBody = document.getElementById("table-body");
    const resultsTableHead = document.getElementById("table-head");

    if (!searchInput || !resultsTableBody || !fieldSelect || !searchButton || !searchForm || !resultsTableHead) {
        console.error("Some expected elements were not found on this page.");
    } else {
        searchInput.addEventListener("input", function () {
            performSearch(searchInput.value, fieldSelect.value);
        });

        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                performSearch(searchInput.value, fieldSelect.value);
            }
        });

        function performSearch(query, field, exact = false) {
            let currentPath = window.location.pathname;
            let endpoint = "/search_students"; // default

            if (query === "") {
                if (currentPath.includes("/courses")) {
                    endpoint = "/all_courses";
                } else if (currentPath.includes("/colleges")) {
                    endpoint = "/all_colleges";
                } else {
                    endpoint = "/all_students";
                }

                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => renderResults(data, "No data available"))
                    .catch(error => console.error("Error fetching all data:", error));

                return;
            }

            if (currentPath.includes("/courses")) {
                endpoint = "/search_courses";
            } else if (currentPath.includes("/colleges")) {
                endpoint = "/search_colleges";
            }

            fetch(`${endpoint}?query=${encodeURIComponent(query)}&field=${encodeURIComponent(field)}&exact=${exact}`)
                .then(response => response.json())
                .then(data => renderResults(data, "No results found"))
                .catch(error => console.error("Error fetching search results:", error));
        }

        function renderResults(data, emptyMessage) {
            resultsTableBody.innerHTML = "";

            if (data.length === 0) {
                resultsTableBody.innerHTML = `<tr><td colspan="6">${emptyMessage}</td></tr>`;
                return;
            }

            data.forEach(row => {
                let htmlRow = "<tr>";
                for (let value of Object.values(row)) {
                    htmlRow += `<td>${value}</td>`;
                }
                htmlRow += "</tr>";
                resultsTableBody.innerHTML += htmlRow;
            });
        }
    }

    // ================== Add Modal ==================
    const modal = document.getElementById("modal");
    const openBtn = document.getElementById("open-modal-btn");
    const closeBtn = document.querySelector(".close");

    if (modal && openBtn && closeBtn) {
        openBtn.addEventListener("click", () => {
            modal.style.display = "block";
        });

        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });

        window.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });

        // Handle form errors opening modal
        const errorScript = document.getElementById("form-errors-json");
        if (errorScript) {
            try {
                const formErrors = JSON.parse(errorScript.textContent);
                if (Object.keys(formErrors).length > 0) {
                    modal.style.display = "block";
                }
            } catch (e) {
                console.error("Failed to parse form errors JSON", e);
            }
        }
    } else {
        console.warn("Modal elements not found on the page.");
    }


    
        const updateButtons = document.querySelectorAll('.update-btn');
    
        updateButtons.forEach(button => {
            button.addEventListener('click', function () {
                const entity = button.dataset.entity;
                let modal;
    
                if (entity === 'student') {
                    modal = document.getElementById('updateStudentModal');
                    document.getElementById('update-id-display').value = button.dataset.id;
                    document.getElementById('update-first-name').value = button.dataset.first_name;
                    document.getElementById('update-last-name').value = button.dataset.last_name;
                    document.getElementById('update-year-level').value = button.dataset.year_level;
                    document.getElementById('update-course-code').value = button.dataset.course_code;
                    document.getElementById('update-gender').value = button.dataset.gender;
                } else if (entity === 'course') {
                    modal = document.getElementById('updateCourseModal');
                    document.getElementById('update-course-id').value = button.dataset.id;
                    document.getElementById('update-course-name').value = button.dataset.name;
                    document.getElementById('update-course-description').value = button.dataset.description;
                } else if (entity === 'college') {
                    modal = document.getElementById('updateCollegeModal');
                    document.getElementById('update-college-id').value = button.dataset.id;
                    document.getElementById('update-college-name').value = button.dataset.name;
                }
    
                if (modal) {
                    modal.style.display = 'block';
                }
            });
        });
    
        // Attach modal close logic ONCE
        document.querySelectorAll('.modal').forEach(modal => {
            const closeBtn = modal.querySelector('.close-update');
            if (closeBtn) {
                closeBtn.addEventListener('click', function () {
                    modal.style.display = 'none';
                });
            }
    
            window.addEventListener('click', function (event) {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });

    
});
