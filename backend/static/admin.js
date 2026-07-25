// =======================================
// AI Mentoring System Admin JS
// Part 1
// =======================================

// ---------------------------------------
// VIEW STUDENT
// ---------------------------------------

function viewStudent(studentId) {

    fetch("/admin/student/" + studentId)

        .then(response => {

            if (!response.ok) {
                throw new Error("Unable to load student.");
            }

            return response.json();

        })

        .then(student => {

            document.getElementById("viewStudentID").textContent =
                student.StudentID || "-";

            document.getElementById("viewProgram").textContent =
                student.Program || "-";

            document.getElementById("viewSemester").textContent =
                String(student.Semester);

            document.getElementById("viewAttendance").textContent =
                (student.Attendance ?? "-") + "%";

            document.getElementById("viewGPA").textContent =
                student.GPA || "-";

            let risk = "Low Risk";

            if (student.Attendance < 75 || student.GPA < 6) {
                risk = "High Risk";
            }

            document.getElementById("viewRisk").textContent = risk;

            document.getElementById("viewRecommendation").textContent =
                student.AIRecommendation || "No AI recommendation available.";

            const modal = new bootstrap.Modal(
                document.getElementById("viewStudentModal")
            );

            modal.show();

        })

        .catch(error => {

            console.error(error);

            alert("Unable to load student details.");

        });

}

// ---------------------------------------
// SEARCH STUDENT
// ---------------------------------------

document.addEventListener("DOMContentLoaded", function () {

    const search = document.getElementById("searchStudent");

    if (search) {

        search.addEventListener("keyup", function () {

            const value = this.value.toLowerCase();

            document.querySelectorAll("tbody tr").forEach(row => {

                row.style.display =
                    row.innerText.toLowerCase().includes(value)
                        ? ""
                        : "none";

            });

        });

    }

});

// ---------------------------------------
// DARK MODE
// ---------------------------------------

document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("themeToggle");

    if (!btn) return;

    btn.addEventListener("click", function () {

        document.body.classList.toggle("dark-mode");

        const icon = btn.querySelector("i");

        if (document.body.classList.contains("dark-mode")) {

            icon.classList.remove("bi-moon-fill");
            icon.classList.add("bi-sun-fill");

        } else {

            icon.classList.remove("bi-sun-fill");
            icon.classList.add("bi-moon-fill");

        }

    });

});
// =======================================
// PART 2
// ADD STUDENT
// =======================================

document.addEventListener("DOMContentLoaded", function () {

    const addForm = document.getElementById("addStudentForm");

    if (!addForm) return;

    addForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const formData = new FormData();

        formData.append("StudentID", document.getElementById("addStudentID").value);
        formData.append("Program", document.getElementById("addProgram").value);
        formData.append("Semester", document.getElementById("addSemester").value);

        // Required by your app.py
        formData.append("Age", 20);

        formData.append("Attendance", document.getElementById("addAttendance").value);
        formData.append("GPA", document.getElementById("addGPA").value);

        // Required by your app.py
        formData.append("AssignmentsCompletion", 100);
        formData.append("EngagementScore", 100);

        fetch("/student/add", {

            method: "POST",
            body: formData

        })

            .then(response => {

                if (response.ok) {

                    alert("Student Added Successfully!");

                    location.reload();

                } else {

                    alert("Unable to add student.");

                }

            })

            .catch(error => {

                console.error(error);

                alert("Server Error.");

            });

    });

});
// =======================================
// PART 3
// EDIT STUDENT
// =======================================

// Open Edit Modal
function editStudent(studentId) {

    fetch("/admin/student/" + studentId)

        .then(response => {

            if (!response.ok) {
                throw new Error("Unable to load student.");
            }

            return response.json();

        })

        .then(student => {

            document.getElementById("editStudentID").value = student.StudentID || "";
            document.getElementById("editProgram").value = student.Program || "";
            document.getElementById("editSemester").value = student.Semester || "";
            document.getElementById("editAttendance").value = student.Attendance || "";
            document.getElementById("editGPA").value = student.GPA || "";

            const modal = new bootstrap.Modal(
                document.getElementById("editStudentModal")
            );

            modal.show();

        })

        .catch(error => {

            console.error(error);
            alert("Unable to load student details.");

        });

}


// Save Changes
document.addEventListener("DOMContentLoaded", function () {

    const editForm = document.getElementById("editStudentForm");

    if (!editForm) return;

    editForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const formData = new FormData();

        formData.append("StudentID",
            document.getElementById("editStudentID").value);

        formData.append("Program",
            document.getElementById("editProgram").value);

        formData.append("Semester",
            document.getElementById("editSemester").value);

        formData.append("Attendance",
            document.getElementById("editAttendance").value);

        formData.append("GPA",
            document.getElementById("editGPA").value);

        fetch("/student/edit", {

            method: "POST",
            body: formData

        })

            .then(response => {

                if (response.ok) {

                    alert("Student Updated Successfully!");

                    location.reload();

                } else {

                    alert("Unable to update student.");

                }

            })

            .catch(error => {

                console.error(error);

                alert("Server Error.");

            });

    });

});
// =======================================
// PART 4
// DELETE STUDENT + UTILITIES
// =======================================

let selectedStudentId = null;

// ----------------------------
// Open Delete Modal
// ----------------------------
function deleteStudent(studentId) {

    selectedStudentId = studentId;

    document.getElementById("deleteStudentID").textContent = studentId;

    const modal = new bootstrap.Modal(
        document.getElementById("deleteModal")
    );

    modal.show();
}


// ----------------------------
// Confirm Delete
// ----------------------------
document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("confirmDeleteBtn");

    if (!btn) {
        console.log("Delete button not found");
        return;
    }

    btn.onclick = function () {

        if (!selectedStudentId) {
            alert("No student selected.");
            return;
        }

        console.log("Deleting Student:", selectedStudentId);

        fetch("/student/delete", {

            method: "POST",

            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },

            body: "StudentID=" + encodeURIComponent(selectedStudentId)

        })

            .then(response => response.json())

            .then(data => {

                alert(data.message);

                location.reload();

            })

            .catch(error => {

                console.error(error);

                alert("Delete Failed");

            });

    };

});

// ----------------------------
// Dashboard Charts
// ----------------------------
document.addEventListener("DOMContentLoaded", function () {

    const attendanceCanvas = document.getElementById("attendanceChart");

    if (attendanceCanvas) {

        new Chart(attendanceCanvas, {

            type: "bar",

            data: {

                labels: ["Excellent", "Good", "Average", "Poor"],

                datasets: [{

                    label: "Attendance",

                    data: [40, 30, 20, 10]

                }]

            }

        });

    }


    const riskCanvas = document.getElementById("riskChart");

    if (riskCanvas) {

        new Chart(riskCanvas, {

            type: "pie",

            data: {

                labels: ["Low", "Medium", "High"],

                datasets: [{

                    data: [60, 25, 15]

                }]

            }

        });

    }

});


// ----------------------------
// Utilities
// ----------------------------
function showSuccess(message) {
    alert(message);
}

function showError(message) {
    alert(message);
}

console.log("Admin JS Loaded Successfully");
document.getElementById("searchStudent").addEventListener("keyup", function () {
    let value = this.value.toLowerCase();
    document.querySelectorAll("tbody tr").forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(value)
            ? ""
            : "none";
    });
});
// =======================================
// Search + Filters
// =======================================

document.addEventListener("DOMContentLoaded", function () {

    const search = document.getElementById("searchStudent");
    const program = document.getElementById("programFilter");
    const semester = document.getElementById("semesterFilter");
    const risk = document.getElementById("riskFilter");

    function filterStudents() {

        const searchValue = search.value.toLowerCase();
        const programValue = program.value.toLowerCase();
        const semesterValue = semester.value;
        const riskValue = risk.value.toLowerCase();

        document.querySelectorAll("#studentTable tr").forEach(row => {

            const id = row.querySelector(".student-id").textContent.toLowerCase();
            const prog = row.querySelector(".program").textContent.toLowerCase();
            const sem = row.querySelector(".semester").textContent.trim();
            console.log("Selected Semester:", semesterValue);
            console.log("Row Semester:", sem);
            console.log("Equal?", semesterValue === sem);
            const riskText = row.querySelector(".risk").textContent.trim().toLowerCase();

            const matchSearch =
                id.includes(searchValue) ||
                prog.includes(searchValue);

            const matchProgram =
                programValue === "" || prog === programValue;

            const matchSemester =
                semesterValue === "" || sem === semesterValue;

            const matchRisk =
                riskValue === "" || riskText.includes(riskValue);

            row.style.display =
                (matchSearch &&
                    matchProgram &&
                    matchSemester &&
                    matchRisk)
                    ? ""
                    : "none";

        });

    }

    search.addEventListener("keyup", filterStudents);
    program.addEventListener("change", filterStudents);
    semester.addEventListener("change", filterStudents);
    risk.addEventListener("change", filterStudents);

});
$(document).ready(function () {

    $("#studentTableData").DataTable({

        pageLength: 10,

        lengthMenu: [
            [10,25,50,100,-1],
            [10,25,50,100,"All"]
        ],

        ordering: true,

        searching: true,

        paging: true,

        info: true,

        responsive: true,

        dom: 'Blfrtip',

        buttons: [

            'copy',

            'csv',

            'excel',

            'pdf',

            'print'

        ]

    });

});