document.addEventListener("DOMContentLoaded", function () {
      console.log("DOM fully loaded and parsed");
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

        searchForm.addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent full page reload
        performSearch(searchInput.value.trim(), fieldSelect.value);
    });

        resultsTableBody.addEventListener('click', function(event) {
        const button = event.target.closest('.delete-btn');
        if (button) {
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
        }
    });


        // Detect entity from current URL
    function getEntityFromPath() {
        const path = window.location.pathname;
        if (path.includes("/students")) return "student";
        if (path.includes("/courses")) return "course";
        if (path.includes("/colleges")) return "college";
        return "student"; // default fallback
    }

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
    const entity = getEntityFromPath();
    let endpoint = "";

    // 🧹 If search input is cleared
    if (!query.trim()) {
        // Reset dropdown to default
        if (fieldSelect) {
            if (entity === "student") fieldSelect.value = "id";
            else if (entity === "course") fieldSelect.value = "course_code";
            else if (entity === "college") fieldSelect.value = "college_code";
        }

        // Load all data for that entity
        if (entity === "student") endpoint = "/all_students";
        else if (entity === "course") endpoint = "/all_courses";
        else if (entity === "college") endpoint = "/all_colleges";

        fetch(endpoint)
            .then(res => res.json())
            .then(data => renderResults(data, entity, "No data available"))
            .catch(err => console.error("Error loading full dataset:", err));

        return; // exit early
    }

    // Normal filtered search
    if (entity === "student") endpoint = "/search_students";
    else if (entity === "course") endpoint = "/search_courses";
    else if (entity === "college") endpoint = "/search_colleges";

    fetch(`${endpoint}?query=${encodeURIComponent(query)}&field=${encodeURIComponent(field)}&exact=${exact}`)
        .then(res => res.json())
        .then(data => renderResults(data, entity, "No results found"))
        .catch(err => console.error("Error fetching search results:", err));
}

    function renderResults(data, entity, emptyMessage) {
        resultsTableBody.innerHTML = "";
        refreshCsrfToken();

        if (!data.length) {
            // colspan depends on entity
            let colspan = 0;
            if (entity === "student") colspan = 8;
            else if (entity === "course") colspan = 4;
            else if (entity === "college") colspan = 3;

            resultsTableBody.innerHTML = `<tr><td colspan="${colspan}">${emptyMessage}</td></tr>`;
            return;
        }

        data.forEach(row => {
            let htmlRow = "<tr>";

            if (entity === "student") {
                // Assuming row keys: id, first_name, last_name, year_level, course_code, gender, photo_url
                htmlRow += `<td>${row.id}</td>`;

                // Photo cell
                const photoSrc = row.prof_pic || '/static/images/default-avatar.png';

                htmlRow += `<td><img src="${photoSrc}" alt="Profile Pic" class="profile-pic" style="height:50px; width:50px; object-fit:cover; border-radius:50%;"></td>`;

                htmlRow += `<td>${row.first_name}</td>`;
                htmlRow += `<td>${row.last_name}</td>`;
                htmlRow += `<td>${row.year_level}</td>`;
                htmlRow += `<td>${row.course_code}</td>`;
                htmlRow += `<td>${row.gender}</td>`;

                // Actions
                htmlRow += `<td>
                    <button class="update-btn custom-btn" data-entity="student"
                            data-id="${row.id}"
                            data-prof-pic="${photoSrc}"
                            data-first_name="${row.first_name}"
                            data-last_name="${row.last_name}"
                            data-year_level="${row.year_level}"
                            data-course_code="${row.course_code}"
                            data-gender="${row.gender}">
                        <i class="fas fa-edit"></i>
                    </button>

                    <form action="/students/delete/${encodeURIComponent(row.id)}" method="post" class="delete-form" style="display:inline;">
                        <input type="hidden" name="csrf_token" value="${window.csrfToken}">
                        <button type="button" class="custom-btn btn-outline-danger delete-btn">
                            <i class="fa fa-trash text-danger" style="color:red;"></i>
                        </button>
                    </form>
                </td>`;
            }
            else if (entity === "course") {
                // row keys: course_code, course_name, college_code
                htmlRow += `<td>${row.course_code}</td>`;
                htmlRow += `<td>${row.course_name}</td>`;
                htmlRow += `<td>${row.college_code}</td>`;

                htmlRow += `<td>
                    <button class="update-btn custom-btn" data-entity="course"
                            data-course-code="${row.course_code}"
                            data-course-name="${row.course_name}"
                            data-college-code="${row.college_code}">
                        <i class="bi bi-pencil-square text-primary"></i>
                    </button>

                    <form action="/courses/delete/${encodeURIComponent(row.course_code)}" method="post" class="delete-form" style="display:inline;">
                        <input type="hidden" name="csrf_token" value="${window.csrfToken}">
                        <button type="button" class="custom-btn btn-outline-danger delete-btn">
                            <i class="fa fa-trash text-danger" style="color:red;"></i>
                        </button>
                    </form>
                </td>`;
            }
            else if (entity === "college") {
                // row keys: college_code, college_name
                htmlRow += `<td>${row.college_code}</td>`;
                htmlRow += `<td>${row.college_name}</td>`;

                htmlRow += `<td>
                    <button class="update-btn custom-btn" data-entity="college"
                            data-college-code="${row.college_code}"
                            data-college-name="${row.college_name}">
                        <i class="fas fa-edit"></i>
                    </button>

                    <form action="/colleges/delete/${encodeURIComponent(row.college_code)}" method="post" class="delete-form" style="display:inline;">
                        <input type="hidden" name="csrf_token" value="${window.csrfToken}">
                        <button type="button" class="custom-btn btn-outline-danger delete-btn">
                            <i class="fa fa-trash text-danger" style="color:red;"></i>
                        </button>
                    </form>
                </td>`;
            }

            htmlRow += "</tr>";
            resultsTableBody.innerHTML += htmlRow;
  
        });
        attachButtonListeners();
        attachDeleteListeners();
    }



    function attachButtonListeners() {
        // Update buttons
        const updateButtons = document.querySelectorAll('.update-btn');
        const updateForm = document.querySelector('#updateStudentModal form');
        const currentCsrfToken = "{{ csrf_token() }}";

        updateButtons.forEach(button => {
            button.addEventListener('click', function () {
                const entity = button.dataset.entity;
                const updateErrorScript = document.getElementById("update-form-errors-json");
                let modal;

                if (entity === 'student') {
                    modal = document.getElementById('updateStudentModal');

                    // Populate fields
                    const id = button.dataset.id;
                    const firstName = button.dataset.first_name;
                    const lastName = button.dataset.last_name;
                    const yearLevel = button.dataset.year_level;
                    const courseCode = button.dataset.course_code;
                    const gender = button.dataset.gender;
                    const profPic = button.dataset.profPic;

                    document.getElementById('update-id').value = id;
                    document.getElementById('original-id').value = id;

                    const updateFirstNameInput = document.getElementById('update-first-name');
                    const updateLastNameInput = document.getElementById('update-last-name');

                    updateFirstNameInput.value = firstName;
                    updateLastNameInput.value = lastName;
                    document.getElementById('update-year-level').value = yearLevel;
                    document.getElementById('update-course-code').value = courseCode;
                    document.getElementById('update-gender').value = gender;

                    const preview = document.getElementById('update-profile-pic-preview');
                    preview.src = profPic && profPic !== "None"
                        ? (profPic.startsWith("http") ? profPic : `/static/uploads/${profPic}`)
                        : "{{ url_for('static', filename='images/default-avatar.png') }}";

                    // Auto-format name on blur
                    updateFirstNameInput.addEventListener('blur', function () {
                        if (this.value) {
                            this.value = this.value
                                .split(' ')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                                .join(' ');
                            showHint(this, "Auto-formatting first name...");
                        }
                    });

                    updateLastNameInput.addEventListener('blur', function () {
                        if (this.value) {
                            this.value = this.value
                                .split(' ')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
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

                // Hide hidden fields visually (if needed)
                if (modal) {
                    const hiddenInputs = modal.querySelectorAll('input[type="hidden"]');
                    hiddenInputs.forEach(input => {
                        input.style.display = 'none';
                    });
                    modal.style.display = 'block';
                }

                // Re-open modal if errors are present after POST
                if (updateErrorScript) {
                    try {
                        const updateFormErrors = JSON.parse(updateErrorScript.textContent);
                        if (Object.keys(updateFormErrors).length > 0 && modal) {
                            modal.style.display = "block";
                        }
                    } catch (e) {
                        console.error("Failed to parse update form errors JSON", e);
                    }
                }
            });
        });
    }

    function attachDeleteListeners() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
        // Remove previous listeners
        button.replaceWith(button.cloneNode(true));
    });

    document.querySelectorAll('.delete-btn').forEach(button => {
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
                    // Inject the latest CSRF token before submitting the form
                    form.querySelector("input[name='csrf_token']").value = window.csrfToken;

                    // Submit the form
                    form.submit();
                }
            });
        });
    });
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

                // Populate fields
                const id = button.dataset.id;
                const firstName = button.dataset.first_name;
                const lastName = button.dataset.last_name;
                const yearLevel = button.dataset.year_level;
                const courseCode = button.dataset.course_code;
                const gender = button.dataset.gender;
                const profPic = button.dataset.profPic;

                document.getElementById('update-id').value = id;
                document.getElementById('original-id').value = id;

                const updateFirstNameInput = document.getElementById('update-first-name');
                const updateLastNameInput = document.getElementById('update-last-name');

                updateFirstNameInput.value = firstName;
                updateLastNameInput.value = lastName;
                document.getElementById('update-year-level').value = yearLevel;
                document.getElementById('update-course-code').value = courseCode;
                document.getElementById('update-gender').value = gender;

                const preview = document.getElementById('update-profile-pic-preview');
                preview.src = profPic && profPic !== "None"
                    ? (profPic.startsWith("http") ? profPic : `/static/uploads/${profPic}`)
                    : "{{ url_for('static', filename='images/default-avatar.png') }}";

                // Auto-format name on blur
                updateFirstNameInput.addEventListener('blur', function () {
                    if (this.value) {
                        this.value = this.value
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                            .join(' ');
                        showHint(this, "Auto-formatting first name...");
                    }
                });

                updateLastNameInput.addEventListener('blur', function () {
                    if (this.value) {
                        this.value = this.value
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
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

            // Hide hidden fields visually (if needed)
            if (modal) {
                const hiddenInputs = modal.querySelectorAll('input[type="hidden"]');
                hiddenInputs.forEach(input => {
                    input.style.display = 'none';
                });
                modal.style.display = 'block';
            }

            // Re-open modal if errors are present after POST
            if (updateErrorScript) {
                try {
                    const updateFormErrors = JSON.parse(updateErrorScript.textContent);
                    if (Object.keys(updateFormErrors).length > 0 && modal) {
                        modal.style.display = "block";
                    }
                } catch (e) {
                    console.error("Failed to parse update form errors JSON", e);
                }
            }
        });
    });

    // Close modal logic
    document.querySelectorAll('.close-update').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('updateStudentModal').style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        const modal = document.getElementById('updateStudentModal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Optional hint function
    function showHint(input, message) {
        const hint = input.nextElementSibling;
        if (hint && hint.classList.contains('hint-text')) {
            hint.textContent = message;
            setTimeout(() => hint.textContent = '', 2000);
        }
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



    // Handle preview and upload logic
    function handleProfilePicChange(inputId, previewId) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);

        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });

        // Allow clicking the preview to trigger file select
        preview.addEventListener('click', function() {
            input.click();
        });



        // Allow clicking the preview to trigger file select
        preview.addEventListener('click', function() {
            input.click();
        });
    }

    // Initialize event listeners
    handleProfilePicChange('add-profile-pic-input', 'add-profile-pic-preview');
    handleProfilePicChange('update-profile-pic-input', 'update-profile-pic-preview');

        // ================== Profile Picture Modal ==================
    const profilePicModal = document.getElementById('profile-pic-modal');
    const profilePicModalImg = document.getElementById('profile-pic-modal-img');
    const closeProfilePicModal = document.getElementById('close-profile-pic-modal');

    document.querySelectorAll('.clickable-pic').forEach(img => {
        img.addEventListener('click', function () {
            profilePicModalImg.src = this.src;
            profilePicModal.style.display = 'block';
        });
    });

    closeProfilePicModal.addEventListener('click', function () {
        profilePicModal.style.display = 'none';
    });

    // Close modal if clicking outside image
    window.addEventListener('click', function (e) {
        if (e.target === profilePicModal) {
            profilePicModal.style.display = 'none';
        }
    });



        // Handle opening the image in modal
        document.querySelectorAll('.profile-pic').forEach(img => {
            img.addEventListener('click', function() {
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                modal.style.display = "block";
                modalImg.src = this.src;
            });
        });

        // Handle closing the modal
        document.querySelector('.image-modal .close').addEventListener('click', function() {
            document.getElementById('imageModal').style.display = "none";
        });

        // Close modal when clicking outside the image
        document.getElementById('imageModal').addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = "none";
            }
        });


document.getElementById('students-rows-per-page').addEventListener('change', (e) => {
  let rows = parseInt(e.target.value);
  if (!rows || rows < 1) rows = 10;  // fallback default

  // Get current URL and update query params
  const url = new URL(window.location.href);
  url.searchParams.set('rows', rows);
  url.searchParams.set('page', 1); // reset to first page

  window.location.href = url.toString();
});

document.addEventListener("DOMContentLoaded", function () {
    const MAX_FILE_SIZE_MB = 2;
    const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

    function showNotification(form, message) {
        // Check if notification div exists, else create it
        let notif = form.querySelector(".file-size-notif");
        if (!notif) {
            notif = document.createElement("div");
            notif.className = "file-size-notif";
            notif.style.color = "red";
            notif.style.marginTop = "0.5em";
            notif.style.fontWeight = "bold";
            form.appendChild(notif);
        }
        notif.textContent = message;
    }

    function clearNotification(form) {
        const notif = form.querySelector(".file-size-notif");
        if (notif) {
            notif.textContent = "";
        }
    }

    function validateFileSize(event) {
        const form = event.target;
        const fileInput = form.querySelector('input[type="file"][name="prof_pic"]');

        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            if (file.size > MAX_FILE_SIZE_BYTES) {
                event.preventDefault();
                showNotification(form, `Profile picture must be less than ${MAX_FILE_SIZE_MB}MB.`);
            } else {
                clearNotification(form);
            }
        } else {
            clearNotification(form);
        }
    }

    const addForm = document.getElementById("add-student-form");
    const updateForm = document.getElementById("update-student-form");

    if (addForm) {
        addForm.addEventListener("submit", validateFileSize);
    }

    if (updateForm) {
        updateForm.addEventListener("submit", validateFileSize);
    }
});


const errorBox = document.getElementById("file-error");
if (errorBox) {
    errorBox.innerText = `Profile picture must be less than ${MAX_FILE_SIZE_MB}MB.`;
    errorBox.classList.remove("d-none");
}


function clearAddProfilePic() {
    const input = document.getElementById('add-profile-pic-input');
    const preview = document.getElementById('add-profile-pic-preview');
    input.value = '';
    preview.src = "{{ url_for('static', filename='images/default-avatar.png') }}";
}

function clearUpdateProfilePic() {
    const input = document.getElementById('update-profile-pic-input');
    const preview = document.getElementById('update-profile-pic-preview');
    input.value = '';
    preview.src = "{{ url_for('static', filename='images/default-avatar.png') }}";

    // Signal to backend to delete the old picture
    document.getElementById('clear-update-pic-flag').value = '1';
}

  window.onload = function() {
    var modal = new bootstrap.Modal(document.getElementById('updateStudentModal'));
    modal.show();
  }

  async function getCsrfToken() {
  const response = await fetch("/get_csrf_token"); // create this route if needed
  const data = await response.json();
  return data.csrf_token;
}

// Handle file input change event
    document.getElementById('add-profile-pic-input').addEventListener('change', function(event) {
        const preview = document.getElementById('add-profile-pic-preview');
        const file = event.target.files[0];

        if (file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                preview.src = e.target.result; // Update the preview image
            };

            reader.readAsDataURL(file); // Convert the image file to a base64 string
        } else {
            preview.src = "{{ url_for('static', filename='images/default-avatar.png') }}"; // Set default image if no file is selected
        }
    });

    // Clear profile picture functionality
    function clearAddProfilePic() {
        document.getElementById('add-profile-pic-input').value = ''; // Clear input
        document.getElementById('add-profile-pic-preview').src = "{{ url_for('static', filename='images/default-avatar.png') }}"; // Reset preview to default
    }

async function refreshCsrfToken() {
  const response = await fetch("/get_csrf_token");
  const data = await response.json();
  window.csrfToken = data.csrf_token;
}
