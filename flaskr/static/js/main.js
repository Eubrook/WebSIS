document.addEventListener("DOMContentLoaded", function () {
    // ================== Search Elements ==================
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const fieldSelect = document.getElementById('search-field');
    const searchButton = document.getElementById('search-button');
    const resultsTableBody = document.getElementById("table-body");
    const resultsTableHead = document.getElementById("table-head");

    // if (!searchInput || !resultsTableBody || !fieldSelect || !searchButton || !searchForm || !resultsTableHead) {
    //     // Silently skip if expected elements are not found on this page
    //     return;
    // } else {
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
        // ================== Add Modal ==================
        const modal = document.getElementById("modal");
        const openBtn = document.getElementById("open-modal-btn");
        const closeBtn = modal ? modal.querySelector(".close") : null;
        const collegeCodeInput = document.getElementById('college_code');
        const firstNameInput = document.getElementById('first_name');
        const lastNameInput = document.getElementById('last_name');

        function showHint(inputElement, message) {
            let hint = inputElement.nextElementSibling;
            if (!hint || !hint.classList.contains('hint-message')) {
                hint = document.createElement('div');
                hint.classList.add('hint-message');
                hint.style.fontSize = "0.8rem";
                hint.style.color = "gray";
                hint.style.marginTop = "3px";
                hint.style.transition = "opacity 0.5s";
                inputElement.parentNode.insertBefore(hint, inputElement.nextSibling);
            }
            hint.textContent = message;
            hint.style.opacity = 1;

            setTimeout(() => {
                hint.style.opacity = 0;
            }, 1500); // fades out after 1.5 seconds
        }

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

            // Uppercase college code
            if (collegeCodeInput) {
                collegeCodeInput.addEventListener('input', function () {
                    this.value = this.value.toUpperCase();
                });
            }

            // Capitalize first letter of each word for first name
            if (firstNameInput) {
                firstNameInput.addEventListener('blur', function () {
                    if (this.value) {
                        this.value = this.value
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');
                        showHint(this, "Auto-formatting first name...");
                    }
                });
            }

            // Capitalize first letter of each word for last name
            if (lastNameInput) {
                lastNameInput.addEventListener('blur', function () {
                    if (this.value) {
                        this.value = this.value
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');
                        showHint(this, "Auto-formatting last name...");
                    }
                });
            }

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

        // ================== Update Modal ==================
        const updateButtons = document.querySelectorAll('.update-btn');
        const updateForm = document.querySelector('#updateStudentModal form');

        updateButtons.forEach(button => {
            button.addEventListener('click', function () {
                const entity = button.dataset.entity;
                const updateErrorScript = document.getElementById("update-form-errors-json");
                let modal;

                if (entity === 'student') {
                    modal = document.getElementById('updateStudentModal');
                    document.getElementById('update-id').value = button.dataset.id;
                    document.getElementById('original-id').value = button.dataset.id;
                    const updateFirstNameInput = document.getElementById('update-first-name');
                    const updateLastNameInput = document.getElementById('update-last-name');

                    updateFirstNameInput.value = button.dataset.first_name;
                    updateLastNameInput.value = button.dataset.last_name;
                    document.getElementById('update-year-level').value = button.dataset.year_level;
                    document.getElementById('update-course-code').value = button.dataset.course_code;
                    document.getElementById('update-gender').value = button.dataset.gender;

                    // Add auto-format for first and last name on blur (Update Modal)
                    updateFirstNameInput.addEventListener('blur', function () {
                        if (this.value) {
                            this.value = this.value
                                .split(' ')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(' ');
                            showHint(this, "Auto-formatting first name...");
                        }
                    });

                    updateLastNameInput.addEventListener('blur', function () {
                        if (this.value) {
                            this.value = this.value
                                .split(' ')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(' ');
                            showHint(this, "Auto-formatting last name...");
                        }
                    });

                } else if (entity === 'course') {
                    modal = document.getElementById('updateCourseModal');
                    document.getElementById('update-course-code').value = button.dataset.courseCode;
                    document.getElementById('original-course-code').value = button.dataset.courseCode;
                    document.getElementById('update-course-name').value = button.dataset.courseName;
                    document.getElementById('update-college-code').value = button.dataset.collegeCode;
                } else if (entity === 'college') {
                    modal = document.getElementById('updateCollegeModal');
                    document.getElementById('update-college-code').value = button.dataset.collegeCode;
                    document.getElementById('original-college-code').value = button.dataset.collegeCode;
                    document.getElementById('update-college-name').value = button.dataset.collegeName;
                }

                // Hide hidden fields
                if (modal) {
                    const hiddenInputs = modal.querySelectorAll('input[type="hidden"]');
                    hiddenInputs.forEach(input => {
                        input.style.display = 'none';
                    });
                    modal.style.display = 'block';
                }

                // Handle update form errors
                if (updateErrorScript) {
                    try {
                        const updateFormErrors = JSON.parse(updateErrorScript.textContent);
                        if (Object.keys(updateFormErrors).length > 0) {
                            const updateModal = document.getElementById("updateStudentModal");
                            if (updateModal) {
                                updateModal.style.display = "block";
                            }
                        }
                    } catch (e) {
                        console.error("Failed to parse update form errors JSON", e);
                    }
                }
            });
        });





    // ========== Attach form validation only ONCE ========== 
    if (updateForm) {
        updateForm.addEventListener('submit', function (event) {
            const idInput = document.getElementById('update-id');
            const idValue = idInput.value.trim();
            const pattern = /^\d{4}-\d{4}$/;
            const errorDivId = 'update-id-error';

            // Remove existing error message if any
            let existingError = document.getElementById(errorDivId);
            if (existingError) {
                existingError.remove();
            }

            let hasError = false;

            // Check format
            if (!pattern.test(idValue)) {
                hasError = true;
                const errorDiv = document.createElement('div');
                errorDiv.id = errorDivId;
                errorDiv.className = 'error';
                errorDiv.style.color = 'red';
                errorDiv.style.fontSize = '0.9em';
                errorDiv.textContent = 'ID must be in the format YYYY-NNNN (e.g., 2023-1234)';
                idInput.parentNode.appendChild(errorDiv);
            } else {
                // Check year part
                const yearPart = parseInt(idValue.split('-')[0]);
                const currentYear = new Date().getFullYear();

                if (yearPart > currentYear) {
                    hasError = true;
                    const errorDiv = document.createElement('div');
                    errorDiv.id = errorDivId;
                    errorDiv.className = 'error';
                    errorDiv.style.color = 'red';
                    errorDiv.style.fontSize = '0.9em';
                    errorDiv.textContent = 'Year in ID cannot be in the future.';
                    idInput.parentNode.appendChild(errorDiv);
                }
            }

            if (hasError) {
                event.preventDefault(); // Prevent form submit
                const updateModal = document.getElementById("updateStudentModal");
                if (updateModal) {
                    updateModal.style.display = "block"; // Keep modal open
                }
                idInput.focus();
            }
        });
    }



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


// --------- Delete sweetalert
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const form = button.closest('form');

            Swal.fire({
                title: 'Are you sure?',
                text: "This action cannot be undone.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete it!',
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });

