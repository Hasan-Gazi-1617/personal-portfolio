(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var root = document.documentElement;
    var nav = document.querySelector('.navbar-custom');
    var panel = document.getElementById('mainNavbar');
    var toggle = document.querySelector('.nav-menu-toggle');
    var themeMeta = document.querySelector('meta[name="theme-color"]');
    var mobile = window.matchMedia('(max-width: 991.98px)');
    var previousFocus = null;

    function syncTheme() {
      if (themeMeta) themeMeta.content = root.dataset.theme === 'light' ? '#f3faf6' : '#0b1422';
    }
    function closeSubmenus() {
      document.querySelectorAll('.submenu-menu.show').forEach(function (menu) { menu.classList.remove('show'); });
      document.querySelectorAll('.submenu-toggle[aria-expanded="true"]').forEach(function (item) { item.setAttribute('aria-expanded', 'false'); });
    }

    syncTheme();
    document.addEventListener('portfolio-theme-change', syncTheme);
    if (!nav || !panel || !window.bootstrap) return;
    var collapse = window.bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false });

    panel.addEventListener('show.bs.collapse', function () {
      previousFocus = document.activeElement;
      document.body.classList.add('nav-open');
      nav.classList.add('menu-is-open');
    });
    panel.addEventListener('shown.bs.collapse', function () {
      var first = panel.querySelector('a, button');
      if (first) first.focus({ preventScroll: true });
    });
    panel.addEventListener('hide.bs.collapse', closeSubmenus);
    panel.addEventListener('hidden.bs.collapse', function () {
      document.body.classList.remove('nav-open');
      nav.classList.remove('menu-is-open');
      if (previousFocus && document.contains(previousFocus)) previousFocus.focus({ preventScroll: true });
    });

    panel.querySelectorAll('a.nav-link:not(.dropdown-toggle), .dropdown-item:not(.submenu-toggle)').forEach(function (link) {
      link.addEventListener('click', function () { if (mobile.matches) collapse.hide(); });
    });
    document.querySelectorAll('.submenu-toggle').forEach(function (button) {
      button.addEventListener('click', function (event) {
        if (!mobile.matches) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        var menu = button.parentElement.querySelector(':scope > .submenu-menu');
        var open = button.getAttribute('aria-expanded') !== 'true';
        closeSubmenus();
        if (menu && open) { menu.classList.add('show'); button.setAttribute('aria-expanded', 'true'); }
      }, true);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && panel.classList.contains('show')) { event.preventDefault(); collapse.hide(); return; }
      if (event.key !== 'Tab' || !mobile.matches || !panel.classList.contains('show')) return;
      var focusable = Array.from(panel.querySelectorAll('a[href], button:not([disabled])')).filter(function (el) { return el.offsetParent !== null; });
      if (!focusable.length) return;
      var first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });

    var links = Array.from(panel.querySelectorAll('a.nav-link[href*="#"]'));
    var pairs = links.map(function (link) { return [document.getElementById(link.hash.slice(1)), link]; }).filter(function (pair) { return pair[0]; });
    if ('IntersectionObserver' in window && pairs.length) {
      var observer = new IntersectionObserver(function (entries) {
        entries.filter(function (entry) { return entry.isIntersecting; }).forEach(function (entry) {
          links.forEach(function (link) { link.classList.remove('active'); link.removeAttribute('aria-current'); });
          var match = pairs.find(function (pair) { return pair[0] === entry.target; });
          if (match) { match[1].classList.add('active'); match[1].setAttribute('aria-current', 'location'); }
        });
      }, { rootMargin: '-25% 0px -65% 0px' });
      pairs.forEach(function (pair) { observer.observe(pair[0]); });
    }

    function resetDesktop() {
      if (!mobile.matches) { document.body.classList.remove('nav-open'); nav.classList.remove('menu-is-open'); closeSubmenus(); }
    }
    mobile.addEventListener ? mobile.addEventListener('change', resetDesktop) : mobile.addListener(resetDesktop);
    if (toggle) toggle.setAttribute('aria-haspopup', 'true');
  });
})();
