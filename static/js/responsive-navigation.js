(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('.navbar-custom');
    var collapseElement = document.getElementById('mainNavbar');
    var themeMeta = document.querySelector('meta[name="theme-color"]');

    function updateThemeChrome() {
      if (!themeMeta) return;
      themeMeta.content = document.documentElement.dataset.theme === 'light' ? '#f3faf6' : '#0b1422';
    }

    updateThemeChrome();
    document.addEventListener('portfolio-theme-change', updateThemeChrome);

    if (!nav || !collapseElement || !window.bootstrap) return;

    var collapse = window.bootstrap.Collapse.getOrCreateInstance(collapseElement, { toggle: false });
    collapseElement.addEventListener('show.bs.collapse', function () {
      document.body.classList.add('nav-open');
    });
    collapseElement.addEventListener('hidden.bs.collapse', function () {
      document.body.classList.remove('nav-open');
    });

    collapseElement.querySelectorAll('a.nav-link:not(.dropdown-toggle)').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.matchMedia('(max-width: 991.98px)').matches) collapse.hide();
      });
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && collapseElement.classList.contains('show')) collapse.hide();
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 992) {
        document.body.classList.remove('nav-open');
        collapseElement.querySelectorAll('.submenu-menu.show').forEach(function (menu) {
          menu.classList.remove('show');
        });
      }
    }, { passive: true });
  });
})();
