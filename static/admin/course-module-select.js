(function () {
  "use strict";

  function setupModuleDropdown() {
    const courseField = document.getElementById("id_course");
    const moduleField = document.getElementById("id_modules");
    if (!courseField || !moduleField) return;

    let moduleMap = {};
    try {
      moduleMap = JSON.parse(moduleField.dataset.moduleMap || "{}");
    } catch (error) {
      console.error("Unable to load course module options", error);
      return;
    }

    const allOptions = Array.from(moduleField.options).map((option) => ({
      value: option.value,
      text: option.text,
    }));

    function refreshModules() {
      const allowed = moduleMap[courseField.value] || [];
      const selected = new Set(Array.from(moduleField.selectedOptions).map((option) => option.value));
      moduleField.replaceChildren();

      allOptions.forEach((item) => {
        if (!allowed.includes(item.value)) return;
        const option = new Option(item.text, item.value);
        option.selected = selected.has(item.value);
        moduleField.add(option);
      });
    }

    courseField.addEventListener("change", refreshModules);
    refreshModules();
  }

  document.addEventListener("DOMContentLoaded", setupModuleDropdown);
})();