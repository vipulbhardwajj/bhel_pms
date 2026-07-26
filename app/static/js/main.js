/*
 * static/js/main.js
 * -------------------
 * Global JS: sidebar collapse/expand, mobile sidebar toggle, notification
 * bell polling, and DataTables default initialisation for any table with
 * the `.data-table` class.
 */

document.addEventListener("DOMContentLoaded", function () {
  initSidebarToggle();
  initNotificationBell();
  initDataTables();
  initAutoDismissAlerts();
});

/* ---------------------------------------------------------------------
 * Sidebar collapse (desktop) / slide-in (mobile)
 * ------------------------------------------------------------------- */
function initSidebarToggle() {
  const toggleBtn = document.getElementById("sidebarToggle");
  if (!toggleBtn) return;

  toggleBtn.addEventListener("click", function () {
    if (window.innerWidth <= 992) {
      document.body.classList.toggle("sidebar-mobile-open");
    } else {
      document.body.classList.toggle("sidebar-collapsed");
      localStorage.setItem(
        "bhel_sidebar_collapsed",
        document.body.classList.contains("sidebar-collapsed") ? "1" : "0"
      );
    }
  });

  if (localStorage.getItem("bhel_sidebar_collapsed") === "1" && window.innerWidth > 992) {
    document.body.classList.add("sidebar-collapsed");
  }
}

/* ---------------------------------------------------------------------
 * Notification bell: poll unread count, mark-all-read action
 * ------------------------------------------------------------------- */
function initNotificationBell() {
  const badge = document.getElementById("notifUnreadBadge");
  const markReadBtn = document.getElementById("markAllReadBtn");

  function refreshCount() {
    fetch("/api/notifications/unread-count")
      .then((r) => r.json())
      .then((data) => {
        if (!badge) return;
        if (data.count > 0) {
          badge.textContent = data.count;
          badge.classList.remove("d-none");
        } else {
          badge.classList.add("d-none");
        }
      })
      .catch(() => {});
  }

  if (badge) {
    refreshCount();
    setInterval(refreshCount, 60000);
  }

  if (markReadBtn) {
    markReadBtn.addEventListener("click", function (e) {
      e.preventDefault();
      fetch("/api/notifications/mark-all-read", { method: "POST" }).then(() => {
        document.querySelectorAll(".notif-item").forEach((el) => el.classList.add("text-muted"));
        if (badge) badge.classList.add("d-none");
      });
    });
  }
}

/* ---------------------------------------------------------------------
 * DataTables default init for tables flagged with .data-table
 * ------------------------------------------------------------------- */
function initDataTables() {
  if (typeof $ === "undefined" || !$.fn.DataTable) return;
  $(".data-table").each(function () {
    $(this).DataTable({
      pageLength: 15,
      lengthChange: false,
      language: {
        search: "",
        searchPlaceholder: "Quick filter...",
        info: "Showing _START_ to _END_ of _TOTAL_ entries",
        paginate: { previous: "‹", next: "›" },
      },
      order: [],
    });
  });
}

/* ---------------------------------------------------------------------
 * Auto-dismiss flash alerts after a few seconds
 * ------------------------------------------------------------------- */
function initAutoDismissAlerts() {
  document.querySelectorAll(".alert-auto-dismiss").forEach(function (alertEl) {
    setTimeout(function () {
      const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
      alert.close();
    }, 5000);
  });
}

/* ---------------------------------------------------------------------
 * Confirm-before-delete helper used by delete forms across the app
 * ------------------------------------------------------------------- */
function confirmDelete(message) {
  return window.confirm(message || "Are you sure you want to delete this record? This action cannot be undone.");
}
