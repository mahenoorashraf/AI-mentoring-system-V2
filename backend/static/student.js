// =============================
// Student Management JS
// =============================

document.addEventListener("DOMContentLoaded", function () {

    // =============================
    // Live Search
    // =============================

    const searchInput = document.getElementById("searchStudent");

    if (searchInput) {

        searchInput.addEventListener("keyup", function () {

            const value = this.value.toLowerCase();

            const rows = document.querySelectorAll("#studentsTable tbody tr");

            rows.forEach(row => {

                row.style.display = row.innerText.toLowerCase().includes(value)
                    ? ""
                    : "none";

            });

        });

    }

    // =============================
    // Risk Filter
    // =============================

    const riskFilter = document.getElementById("riskFilter");

    if (riskFilter) {

        riskFilter.addEventListener("change", filterTable);

    }

    // =============================
    // Program Filter
    // =============================

    const programFilter = document.getElementById("programFilter");

    if (programFilter) {

        programFilter.addEventListener("change", filterTable);

    }

});


// =============================
// Filter Table
// =============================

function filterTable() {

    const risk = document.getElementById("riskFilter").value.toLowerCase();

    const program = document.getElementById("programFilter").value.toLowerCase();

    const rows = document.querySelectorAll("#studentsTable tbody tr");

    rows.forEach(row => {

        const rowText = row.innerText.toLowerCase();

        let show = true;

        if (risk && !rowText.includes(risk))
            show = false;

        if (program && !rowText.includes(program))
            show = false;

        row.style.display = show ? "" : "none";

    });

}


// =============================
// View Student
// =============================

function viewStudent(studentId) {

    fetch("/admin/student/" + studentId)

        .then(response => response.json())

        .then(student => {

            document.getElementById("studentDetails").innerHTML = `

<table class="table table-bordered">

<tr>
<th>Student ID</th>
<td>${student.StudentID}</td>
</tr>

<tr>
<th>Program</th>
<td>${student.Program}</td>
</tr>

<tr>
<th>Semester</th>
<td>${student.Semester}</td>
</tr>

<tr>
<th>Age</th>
<td>${student.Age}</td>
</tr>

<tr>
<th>Attendance</th>
<td>${student.Attendance}%</td>
</tr>

<tr>
<th>GPA</th>
<td>${student.GPA}</td>
</tr>

<tr>
<th>Assignments</th>
<td>${student.AssignmentsCompletion}</td>
</tr>

<tr>
<th>Engagement</th>
<td>${student.EngagementScore}</td>
</tr>

<tr>
<th>Stress</th>
<td>${student.StressLevel}</td>
</tr>

<tr>
<th>Sleep Hours</th>
<td>${student.SleepHours}</td>
</tr>

<tr>
<th>Mental Wellbeing</th>
<td>${student.MentalWellbeing}</td>
</tr>

</table>

`;

            new bootstrap.Modal(
                document.getElementById("viewStudentModal")
            ).show();

        })

        .catch(error => {

            console.log(error);

            alert("Unable to load student.");

        });

}


// =============================
// Edit Student
// =============================

function editStudent(studentId) {

    fetch("/admin/student/" + studentId)

        .then(res => res.json())

        .then(student => {

            console.log(student);

            document.getElementById("editStudentID").value = student.StudentID;
            document.getElementById("editProgram").value = student.Program;
            document.getElementById("editSemester").value = student.Semester;
            document.getElementById("editAttendance").value = student.Attendance;
            document.getElementById("editGPA").value = student.GPA;

            new bootstrap.Modal(
                document.getElementById("editStudentModal")
            ).show();

        })

        .catch(err => {
            console.error(err);
            alert("Unable to load student.");
        });

}


// =============================
// Delete Student
// =============================

function deleteStudent(id) {

    document.getElementById("deleteStudentID").value = id;

    new bootstrap.Modal(
        document.getElementById("deleteStudentModal")
    ).show();

}


// =============================
// Dark Mode
// =============================

const themeBtn = document.getElementById("themeToggle");

if (themeBtn) {

    themeBtn.addEventListener("click", () => {

        document.body.classList.toggle("dark-mode");

    });

}


// =============================
// Form Validation
// =============================

const addForm = document.querySelector("#addStudentModal form");

if (addForm) {

    addForm.addEventListener("submit", function (e) {

        const studentId = this.StudentID.value.trim();

        const program = this.Program.value.trim();

        if (studentId === "" || program === "") {

            e.preventDefault();

            alert("Please fill all required fields.");

        }

    });

}