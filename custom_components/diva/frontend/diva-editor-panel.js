const PANEL_TEXT = {
  en: {
    title: "DIVA Editor",
    subtitle: "Medical, calendar, and reporting operations from a dedicated sidebar panel.",
    pet: "Pet",
    refresh: "Refresh",
    noPets: "No DIVA pets were discovered. Open the integration first and create at least one pet.",
    medications: "Medication Courses",
    vaccines: "Vaccines",
    reports: "Reports & Calendar",
    addMedication: "Add medication",
    editMedication: "Edit medication",
    remove: "Remove",
    logDose: "Log dose",
    addOverride: "Add override",
    editOverride: "Edit override",
    complete: "Complete",
    reschedule: "Reschedule",
    cancel: "Cancel",
    syncCalendar: "Sync calendar",
    generateVetTxt: "Vet report TXT",
    generateVetPdf: "Vet report PDF",
    generateOpsTxt: "Ops report TXT",
    generateOpsPdf: "Ops report PDF",
    linkedCalendars: "Linked calendars",
    recentReports: "Recent reports",
    conflicts: "Conflicts",
    reviewConflict: "Review conflict",
    resolution: "Resolution",
    divaVersion: "DIVA version",
    calendarVersion: "Calendar version",
    conflictReason: "Reason",
    conflictOccurred: "Detected",
    conflictType: "Conflict type",
    syncKey: "Sync key",
    missingEvent: "No event on this side.",
    divaWins: "DIVA wins",
    calendarWins: "Calendar wins",
    dismissConflict: "Dismiss",
    statusConflictResolved: "Conflict resolution saved.",
    conflictTypes: {
      deleted_external: "Calendar deleted a DIVA event",
      diverged: "Calendar event diverged",
      unmanaged_external: "Calendar has an unmanaged DIVA event",
    },
    empty: "No data",
    working: "Working...",
    statusSuccess: "Action completed.",
    statusError: "Action failed.",
    confirmDeleteMedication: "Remove this medication course?",
    confirmRemoveOverride: "Remove this vaccine override?",
    confirmCancelVaccine: "Cancel this vaccine reminder?",
    confirmCompleteVaccine: "Mark this vaccine as completed?",
    confirm: "Confirm",
    save: "Save",
    close: "Close",
    actor: "Actor",
    note: "Note",
    medicationName: "Medication name",
    dose: "Dose",
    times: "Times",
    startDate: "Start date",
    endDate: "End date",
    route: "Route",
    notes: "Notes",
    vaccineDoseId: "Dose ID",
    vaccineName: "Vaccine name",
    dueDate: "Due date",
    recurrenceMonths: "Recurrence months",
    category: "Category",
    categories: {
      core: "Core",
      non_core: "Non-core",
      regional: "Regional",
      review: "Review",
      vet: "Vet",
    },
    scheduleNote: "Note",
    doseNote: "Dose note",
    timesHelp: "Comma-separated 24h times, e.g. 08:00, 20:00",
    overrideHelp: "Use overrides for one-off due date or recurrence changes.",
    imported: "Imported overrides",
    journal: "Recent journal",
    due: "Due",
    recurrence: "Recurrence",
    source: "Source",
    calendarStatus: "Sync status",
    reportPath: "Path",
    generatedAt: "Generated",
    statusLabel: "Status",
  },
  ru: {
    title: "Редактор DIVA",
    subtitle: "Медицинские, календарные и отчетные операции в отдельной панели.",
    pet: "Питомец",
    refresh: "Обновить",
    noPets: "Питомцы DIVA не найдены. Сначала создайте питомца в интеграции.",
    medications: "Курсы лекарств",
    vaccines: "Прививки",
    reports: "Отчеты и календарь",
    addMedication: "Добавить лекарство",
    editMedication: "Изменить лекарство",
    remove: "Удалить",
    logDose: "Отметить дозу",
    addOverride: "Добавить override",
    editOverride: "Изменить override",
    complete: "Завершить",
    reschedule: "Перенести",
    cancel: "Отменить",
    syncCalendar: "Синхронизировать календарь",
    generateVetTxt: "Vet report TXT",
    generateVetPdf: "Vet report PDF",
    generateOpsTxt: "Ops report TXT",
    generateOpsPdf: "Ops report PDF",
    linkedCalendars: "Связанные календари",
    recentReports: "Последние отчеты",
    conflicts: "Конфликты",
    reviewConflict: "Открыть конфликт",
    resolution: "Решение",
    divaVersion: "Версия DIVA",
    calendarVersion: "Версия календаря",
    conflictReason: "Причина",
    conflictOccurred: "Обнаружен",
    conflictType: "Тип конфликта",
    syncKey: "Sync key",
    missingEvent: "С этой стороны события нет.",
    divaWins: "DIVA главнее",
    calendarWins: "Календарь главнее",
    dismissConflict: "Скрыть",
    statusConflictResolved: "Решение по конфликту сохранено.",
    conflictTypes: {
      deleted_external: "Календарь удалил событие DIVA",
      diverged: "Событие в календаре разошлось с DIVA",
      unmanaged_external: "В календаре есть неуправляемое DIVA-событие",
    },
    empty: "Нет данных",
    working: "Выполняется...",
    statusSuccess: "Действие выполнено.",
    statusError: "Действие завершилось ошибкой.",
    confirmDeleteMedication: "Удалить этот курс лекарства?",
    confirmRemoveOverride: "Удалить этот vaccine override?",
    confirmCancelVaccine: "Отменить это напоминание о прививке?",
    confirmCompleteVaccine: "Отметить прививку как выполненную?",
    confirm: "Подтвердить",
    save: "Сохранить",
    close: "Закрыть",
    actor: "Кто выполнил",
    note: "Заметка",
    medicationName: "Название лекарства",
    dose: "Доза",
    times: "Время приема",
    startDate: "Дата начала",
    endDate: "Дата окончания",
    route: "Способ приема",
    notes: "Заметки",
    vaccineDoseId: "ID дозы",
    vaccineName: "Название прививки",
    dueDate: "Дата",
    recurrenceMonths: "Повтор через месяцев",
    category: "Категория",
    categories: {
      core: "Базовая",
      non_core: "Дополнительная",
      regional: "Региональная",
      review: "Ревью",
      vet: "Вет",
    },
    scheduleNote: "Заметка",
    doseNote: "Заметка по дозе",
    timesHelp: "Время через запятую в 24ч формате, например 08:00, 20:00",
    overrideHelp: "Используйте override для точечного переноса даты или изменения повторяемости.",
    imported: "Импортированные override",
    journal: "Последний журнал",
    due: "Срок",
    recurrence: "Повтор",
    source: "Источник",
    calendarStatus: "Статус синхронизации",
    reportPath: "Путь",
    generatedAt: "Создан",
    statusLabel: "Статус",
  },
  es: {
    title: "Editor DIVA",
    subtitle: "Operaciones médicas, de calendario y de informes desde un panel lateral dedicado.",
    pet: "Mascota",
    refresh: "Actualizar",
    noPets: "No se encontraron mascotas DIVA. Primero crea una mascota en la integración.",
    medications: "Tratamientos",
    vaccines: "Vacunas",
    reports: "Informes y calendario",
    addMedication: "Añadir medicación",
    editMedication: "Editar medicación",
    remove: "Eliminar",
    logDose: "Registrar dosis",
    addOverride: "Añadir override",
    editOverride: "Editar override",
    complete: "Completar",
    reschedule: "Reprogramar",
    cancel: "Cancelar",
    syncCalendar: "Sincronizar calendario",
    generateVetTxt: "Informe vet TXT",
    generateVetPdf: "Informe vet PDF",
    generateOpsTxt: "Informe ops TXT",
    generateOpsPdf: "Informe ops PDF",
    linkedCalendars: "Calendarios vinculados",
    recentReports: "Informes recientes",
    conflicts: "Conflictos",
    reviewConflict: "Revisar conflicto",
    resolution: "Resolución",
    divaVersion: "Versión DIVA",
    calendarVersion: "Versión del calendario",
    conflictReason: "Motivo",
    conflictOccurred: "Detectado",
    conflictType: "Tipo de conflicto",
    syncKey: "Clave sync",
    missingEvent: "No hay evento en este lado.",
    divaWins: "Gana DIVA",
    calendarWins: "Gana calendario",
    dismissConflict: "Descartar",
    statusConflictResolved: "Resolución del conflicto guardada.",
    conflictTypes: {
      deleted_external: "El calendario eliminó un evento de DIVA",
      diverged: "El evento del calendario divergió",
      unmanaged_external: "El calendario contiene un evento DIVA no gestionado",
    },
    empty: "Sin datos",
    working: "Procesando...",
    statusSuccess: "Acción completada.",
    statusError: "La acción falló.",
    confirmDeleteMedication: "¿Eliminar este tratamiento?",
    confirmRemoveOverride: "¿Eliminar este override de vacuna?",
    confirmCancelVaccine: "¿Cancelar este recordatorio de vacuna?",
    confirmCompleteVaccine: "¿Marcar esta vacuna como completada?",
    confirm: "Confirmar",
    save: "Guardar",
    close: "Cerrar",
    actor: "Actor",
    note: "Nota",
    medicationName: "Nombre del medicamento",
    dose: "Dosis",
    times: "Horas",
    startDate: "Fecha de inicio",
    endDate: "Fecha de fin",
    route: "Vía",
    notes: "Notas",
    vaccineDoseId: "ID de dosis",
    vaccineName: "Nombre de vacuna",
    dueDate: "Fecha",
    recurrenceMonths: "Repetición en meses",
    category: "Categoría",
    categories: {
      core: "Core",
      non_core: "No core",
      regional: "Regional",
      review: "Revisión",
      vet: "Vet",
    },
    scheduleNote: "Nota",
    doseNote: "Nota de dosis",
    timesHelp: "Horas separadas por coma en formato 24h, p. ej. 08:00, 20:00",
    overrideHelp: "Usa overrides para cambios puntuales de fecha o recurrencia.",
    imported: "Overrides importados",
    journal: "Diario reciente",
    due: "Vence",
    recurrence: "Recurrencia",
    source: "Fuente",
    calendarStatus: "Estado de sincronización",
    reportPath: "Ruta",
    generatedAt: "Generado",
    statusLabel: "Estado",
  },
};

const CATEGORY_OPTIONS = ["core", "non_core", "regional", "review", "vet"];

const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#39;");

class DivaEditorPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._selectedPetId = null;
    this._dialog = null;
    this._busy = false;
    this._status = null;
  }

  set hass(hass) {
    this._hass = hass;
    const pets = this._collectPets();
    if (!this._selectedPetId || !pets.some((pet) => pet.pet_id === this._selectedPetId)) {
      this._selectedPetId = pets[0]?.pet_id ?? null;
    }
    this._render();
  }

  get _locale() {
    const raw = this._hass?.locale?.language || this._hass?.language || this._hass?.selectedLanguage || "en";
    const normalized = String(raw).toLowerCase();
    if (normalized.startsWith("ru")) {
      return "ru";
    }
    if (normalized.startsWith("es")) {
      return "es";
    }
    return "en";
  }

  t(key) {
    const bundle = PANEL_TEXT[this._locale] || PANEL_TEXT.en;
    return key.split(".").reduce((acc, part) => acc?.[part], bundle) ?? key;
  }

  _collectPets() {
    if (!this._hass) {
      return [];
    }
    const pets = new Map();
    for (const stateObj of Object.values(this._hass.states)) {
      const petId = stateObj.attributes?.pet_id;
      if (!petId) {
        continue;
      }
      const entry = pets.get(petId) || {
        pet_id: petId,
        pet_name: stateObj.attributes.pet_name || petId,
      };
      if (stateObj.attributes.pet_name) {
        entry.pet_name = stateObj.attributes.pet_name;
      }
      pets.set(petId, entry);
    }
    return Array.from(pets.values()).sort((left, right) => left.pet_name.localeCompare(right.pet_name));
  }

  _findState(petId, suffix) {
    if (!this._hass || !petId) {
      return null;
    }
    return Object.values(this._hass.states).find(
      (stateObj) => stateObj.attributes?.pet_id === petId && stateObj.entity_id.endsWith(`_${suffix}`),
    ) || null;
  }

  _selectedPet() {
    return this._collectPets().find((pet) => pet.pet_id === this._selectedPetId) || null;
  }

  _sensorAttrs(petId, suffix) {
    return this._findState(petId, suffix)?.attributes || {};
  }

  _stateValue(petId, suffix) {
    return this._findState(petId, suffix)?.state || "";
  }

  _formatEventMeta(event) {
    if (!event) {
      return this.t("missingEvent");
    }
    const lines = [event.summary || event.event_id || this.t("empty")];
    if (event.start) {
      lines.push(event.start);
    }
    if (event.end) {
      lines.push(event.end);
    }
    if (event.location) {
      lines.push(event.location);
    }
    return lines.join(" • ");
  }

  _openDialog(type, payload = {}) {
    this._dialog = { type, payload };
    this._render();
  }

  _closeDialog() {
    this._dialog = null;
    this._render();
  }

  _setStatus(message, level = "info") {
    this._status = { message, level, ts: Date.now() };
    this._render();
  }

  async _callService(service, data, options = {}) {
    if (!this._hass || !this._selectedPetId) {
      return;
    }
    this._busy = true;
    this._render();
    try {
      await this._hass.callService("diva", service, {
        pet_id: this._selectedPetId,
        ...data,
      });
      this._busy = false;
      this._setStatus(options.successMessage || this.t("statusSuccess"), "success");
      if (options.closeDialog !== false) {
        this._dialog = null;
      }
      this._render();
    } catch (error) {
      const detail = error?.body?.message || error?.message || String(error);
      this._busy = false;
      this._setStatus(`${this.t("statusError")} ${detail}`, "error");
    }
  }

  async _handleMedicationSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    await this._callService("upsert_medication_course", {
      medication_name: form.get("medication_name"),
      dose: form.get("dose") || undefined,
      times: form.get("times") || undefined,
      start_date: form.get("start_date") || undefined,
      end_date: form.get("end_date") || undefined,
      route: form.get("route") || undefined,
      notes: form.get("notes") || undefined,
    });
  }

  async _handleVaccineOverrideSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    const recurrence = form.get("recurrence_months");
    await this._callService("upsert_vaccine_override", {
      vaccine_dose_id: form.get("vaccine_dose_id") || undefined,
      vaccine_name: form.get("vaccine_name") || undefined,
      due_date: form.get("due_date") || undefined,
      recurrence_months: recurrence ? Number(recurrence) : undefined,
      category: form.get("category") || undefined,
      notes: form.get("notes") || undefined,
    });
  }

  async _handleRescheduleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    await this._callService("reschedule_vaccine", {
      vaccine_dose_id: form.get("vaccine_dose_id") || undefined,
      vaccine_name: form.get("vaccine_name") || undefined,
      due_date: form.get("due_date"),
      note: form.get("note") || undefined,
    });
  }

  _renderDialog() {
    if (!this._dialog) {
      return "";
    }
    const payload = this._dialog.payload || {};
    const close = `<button type="button" class="secondary" data-action="close-dialog">${escapeHtml(this.t("close"))}</button>`;
    if (this._dialog.type === "medication") {
      return `
        <div class="dialog-backdrop">
          <div class="dialog">
            <h3>${escapeHtml(payload.medication_name ? this.t("editMedication") : this.t("addMedication"))}</h3>
            <form id="medication-form" class="dialog-form">
              <label>${escapeHtml(this.t("medicationName"))}<input name="medication_name" required value="${escapeHtml(payload.medication_name || "")}"></label>
              <label>${escapeHtml(this.t("dose"))}<input name="dose" value="${escapeHtml(payload.dose || "")}"></label>
              <label>${escapeHtml(this.t("times"))}<input name="times" placeholder="08:00, 20:00" value="${escapeHtml(payload.medication_times || payload.times || "")}"></label>
              <div class="hint">${escapeHtml(this.t("timesHelp"))}</div>
              <label>${escapeHtml(this.t("startDate"))}<input type="date" name="start_date" value="${escapeHtml(payload.start_date || "")}"></label>
              <label>${escapeHtml(this.t("endDate"))}<input type="date" name="end_date" value="${escapeHtml(payload.end_date || "")}"></label>
              <label>${escapeHtml(this.t("route"))}<input name="route" value="${escapeHtml(payload.medication_route || payload.route || "")}"></label>
              <label>${escapeHtml(this.t("notes"))}<textarea name="notes" rows="3">${escapeHtml(payload.notes || "")}</textarea></label>
              <div class="dialog-actions">
                ${close}
                <button type="submit">${escapeHtml(this.t("save"))}</button>
              </div>
            </form>
          </div>
        </div>`;
    }
    if (this._dialog.type === "vaccine_override") {
      const categoryOptions = CATEGORY_OPTIONS.map(
        (option) => `<option value="${option}" ${payload.category === option ? "selected" : ""}>${escapeHtml(this.t(`categories.${option}`))}</option>`,
      ).join("");
      return `
        <div class="dialog-backdrop">
          <div class="dialog">
            <h3>${escapeHtml(payload.vaccine_dose_id || payload.vaccine_name ? this.t("editOverride") : this.t("addOverride"))}</h3>
            <form id="vaccine-override-form" class="dialog-form">
              <label>${escapeHtml(this.t("vaccineDoseId"))}<input name="vaccine_dose_id" value="${escapeHtml(payload.vaccine_dose_id || "")}"></label>
              <label>${escapeHtml(this.t("vaccineName"))}<input name="vaccine_name" value="${escapeHtml(payload.vaccine_name || "")}"></label>
              <label>${escapeHtml(this.t("dueDate"))}<input type="date" name="due_date" value="${escapeHtml(payload.due_date || "")}"></label>
              <label>${escapeHtml(this.t("recurrenceMonths"))}<input type="number" min="1" max="60" name="recurrence_months" value="${escapeHtml(payload.recurrence_months || "")}"></label>
              <label>${escapeHtml(this.t("category"))}
                <select name="category">
                  <option value=""></option>
                  ${categoryOptions}
                </select>
              </label>
              <label>${escapeHtml(this.t("notes"))}<textarea name="notes" rows="3">${escapeHtml(payload.notes || "")}</textarea></label>
              <div class="hint">${escapeHtml(this.t("overrideHelp"))}</div>
              <div class="dialog-actions">
                ${close}
                <button type="submit">${escapeHtml(this.t("save"))}</button>
              </div>
            </form>
          </div>
        </div>`;
    }
    if (this._dialog.type === "reschedule_vaccine") {
      return `
        <div class="dialog-backdrop">
          <div class="dialog">
            <h3>${escapeHtml(this.t("reschedule"))}</h3>
            <form id="vaccine-reschedule-form" class="dialog-form">
              <input type="hidden" name="vaccine_dose_id" value="${escapeHtml(payload.vaccine_dose_id || "")}">
              <input type="hidden" name="vaccine_name" value="${escapeHtml(payload.vaccine_name || "")}">
              <label>${escapeHtml(this.t("dueDate"))}<input type="date" required name="due_date" value="${escapeHtml(payload.due_date || "")}"></label>
              <label>${escapeHtml(this.t("scheduleNote"))}<textarea name="note" rows="3">${escapeHtml(payload.note || "")}</textarea></label>
              <div class="dialog-actions">
                ${close}
                <button type="submit">${escapeHtml(this.t("save"))}</button>
              </div>
            </form>
          </div>
        </div>`;
    }
    if (this._dialog.type === "log_dose") {
      return `
        <div class="dialog-backdrop">
          <div class="dialog">
            <h3>${escapeHtml(this.t("logDose"))}</h3>
            <form id="log-dose-form" class="dialog-form">
              <input type="hidden" name="medication_name" value="${escapeHtml(payload.medication_name || "")}">
              <label>${escapeHtml(this.t("medicationName"))}<input value="${escapeHtml(payload.medication_name || "")}" disabled></label>
              <label>${escapeHtml(this.t("dose"))}<input name="dose" value="${escapeHtml(payload.dose || "")}"></label>
              <label>${escapeHtml(this.t("actor"))}<input name="actor" value="${escapeHtml(payload.actor || "")}"></label>
              <label>${escapeHtml(this.t("doseNote"))}<textarea name="note" rows="3">${escapeHtml(payload.note || "")}</textarea></label>
              <div class="dialog-actions">
                ${close}
                <button type="submit">${escapeHtml(this.t("save"))}</button>
              </div>
            </form>
          </div>
        </div>`;
    }
    if (this._dialog.type === "calendar_conflict") {
      const conflictType = payload.conflict_type ? this.t(`conflictTypes.${payload.conflict_type}`) : this.t("empty");
      return `
        <div class="dialog-backdrop">
          <div class="dialog">
            <h3>${escapeHtml(this.t("conflicts"))}</h3>
            <div class="dialog-form">
              <label>${escapeHtml(this.t("conflictType"))}<input value="${escapeHtml(conflictType)}" disabled></label>
              <label>${escapeHtml(this.t("conflictReason"))}<textarea rows="2" disabled>${escapeHtml(payload.reason || this.t("empty"))}</textarea></label>
              <label>${escapeHtml(this.t("conflictOccurred"))}<input value="${escapeHtml(payload.occurred_at || "")}" disabled></label>
              <label>${escapeHtml(this.t("syncKey"))}<input value="${escapeHtml(payload.sync_key || "")}" disabled></label>
              <label>${escapeHtml(this.t("source"))}<input value="${escapeHtml(payload.calendar_entity_id || "")}" disabled></label>
              <label>${escapeHtml(this.t("divaVersion"))}<textarea rows="3" disabled>${escapeHtml(this._formatEventMeta(payload.effective_event || payload.base_event))}</textarea></label>
              <label>${escapeHtml(this.t("calendarVersion"))}<textarea rows="3" disabled>${escapeHtml(this._formatEventMeta(payload.external_event))}</textarea></label>
            </div>
            <div class="dialog-actions">
              ${close}
              <button type="button" class="secondary" data-action="resolve-calendar-conflict" data-resolution="dismiss">${escapeHtml(this.t("dismissConflict"))}</button>
              <button type="button" class="secondary" data-action="resolve-calendar-conflict" data-resolution="calendar_wins">${escapeHtml(this.t("calendarWins"))}</button>
              <button type="button" data-action="resolve-calendar-conflict" data-resolution="diva_wins">${escapeHtml(this.t("divaWins"))}</button>
            </div>
          </div>
        </div>`;
    }
    if (this._dialog.type === "confirm") {
      return `
        <div class="dialog-backdrop">
          <div class="dialog compact">
            <h3>${escapeHtml(payload.message || "Confirm")}</h3>
            <div class="dialog-actions">
              ${close}
              <button type="button" data-action="confirm-dialog">${escapeHtml(this.t("confirm"))}</button>
            </div>
          </div>
        </div>`;
    }
    return "";
  }

  _renderMedicationSection(petId) {
    const attrs = this._sensorAttrs(petId, "active_medications");
    const courses = attrs.configured_courses || [];
    const overdue = attrs.overdue_medications || [];
    return `
      <section class="card">
        <div class="section-header">
          <div>
            <h2>${escapeHtml(this.t("medications"))}</h2>
            <p>${escapeHtml(overdue.length ? `Overdue: ${overdue.join(", ")}` : this.t("empty"))}</p>
          </div>
          <button data-action="open-medication-add">${escapeHtml(this.t("addMedication"))}</button>
        </div>
        ${courses.length ? `
          <table>
            <thead>
              <tr>
                <th>${escapeHtml(this.t("medicationName"))}</th>
                <th>${escapeHtml(this.t("dose"))}</th>
                <th>${escapeHtml(this.t("times"))}</th>
                <th>${escapeHtml(this.t("startDate"))}</th>
                <th>${escapeHtml(this.t("endDate"))}</th>
                <th>${escapeHtml(this.t("route"))}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${courses.map((course, index) => `
                <tr>
                  <td>${escapeHtml(course.medication_name)}</td>
                  <td>${escapeHtml(course.dose || "")}</td>
                  <td>${escapeHtml(course.medication_times || "")}</td>
                  <td>${escapeHtml(course.start_date || "")}</td>
                  <td>${escapeHtml(course.end_date || "-")}</td>
                  <td>${escapeHtml(course.medication_route || "-")}</td>
                  <td class="actions">
                    <button data-action="edit-medication" data-index="${index}">${escapeHtml(this.t("editMedication"))}</button>
                    <button data-action="log-dose" data-index="${index}">${escapeHtml(this.t("logDose"))}</button>
                    <button class="danger" data-action="remove-medication" data-index="${index}">${escapeHtml(this.t("remove"))}</button>
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
      </section>`;
  }

  _renderVaccineSection(petId) {
    const attrs = this._sensorAttrs(petId, "vaccine_status");
    const plan = attrs.effective_plan || [];
    const overrides = attrs.configured_overrides || [];
    const runtimeOverrides = attrs.vaccine_overrides || {};
    const completed = attrs.completed_vaccine_doses || {};
    const overrideKeys = Object.keys(runtimeOverrides);
    return `
      <section class="card">
        <div class="section-header">
          <div>
            <h2>${escapeHtml(this.t("vaccines"))}</h2>
            <p>${escapeHtml(this._stateValue(petId, "vaccine_status") || this.t("empty"))}</p>
          </div>
          <button data-action="open-vaccine-add">${escapeHtml(this.t("addOverride"))}</button>
        </div>
        ${plan.length ? `
          <table>
            <thead>
              <tr>
                <th>${escapeHtml(this.t("vaccineName"))}</th>
                <th>${escapeHtml(this.t("due"))}</th>
                <th>${escapeHtml(this.t("category"))}</th>
                <th>${escapeHtml(this.t("recurrence"))}</th>
                <th>${escapeHtml(this.t("statusLabel"))}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${plan.map((item, index) => {
                const runtime = runtimeOverrides[item.vaccine_dose_id] || {};
                const status = completed[item.vaccine_dose_id] ? `completed ${completed[item.vaccine_dose_id]}` : (runtime.vaccine_status || "scheduled");
                return `
                  <tr>
                    <td>${escapeHtml(item.vaccine_name)}</td>
                    <td>${escapeHtml(item.due_date)}</td>
                    <td>${escapeHtml(this.t(`categories.${item.category}`))}</td>
                    <td>${escapeHtml(item.recurrence_months ? `${item.recurrence_months}m` : "-")}</td>
                    <td>${escapeHtml(status)}</td>
                    <td class="actions">
                      <button data-action="complete-vaccine" data-index="${index}">${escapeHtml(this.t("complete"))}</button>
                      <button data-action="reschedule-vaccine" data-index="${index}">${escapeHtml(this.t("reschedule"))}</button>
                      <button data-action="cancel-vaccine" data-index="${index}">${escapeHtml(this.t("cancel"))}</button>
                      <button data-action="edit-vaccine-override" data-index="${index}">${escapeHtml(this.t("editOverride"))}</button>
                    </td>
                  </tr>`;
              }).join("")}
            </tbody>
          </table>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
        <div class="subsection">
          <h3>${escapeHtml(this.t("imported"))}</h3>
          ${overrides.length ? `<ul class="list">${overrides.map((item, index) => `
            <li>
              <div>
                <strong>${escapeHtml(item.vaccine_name || item.vaccine_dose_id || "override")}</strong>
                <span>${escapeHtml(item.due_date || "-")}</span>
              </div>
              <div class="actions">
                <button data-action="edit-configured-override" data-index="${index}">${escapeHtml(this.t("editOverride"))}</button>
                <button class="danger" data-action="remove-vaccine-override" data-index="${index}">${escapeHtml(this.t("remove"))}</button>
              </div>
            </li>`).join("")}</ul>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
          ${overrideKeys.length ? `<div class="hint">Runtime overrides: ${escapeHtml(overrideKeys.join(", "))}</div>` : ""}
        </div>
      </section>`;
  }

  _renderReportsSection(petId) {
    const reports = this._sensorAttrs(petId, "generated_reports").reports || [];
    const calendar = this._sensorAttrs(petId, "calendar_sync");
    const conflictState = this._sensorAttrs(petId, "calendar_conflicts");
    const ops = this._sensorAttrs(petId, "operations_center");
    const linkedCalendars = calendar.linked_calendars || [];
    const conflicts = conflictState.conflicts || [];
    const recentJournal = ops.recent_journal || [];
    return `
      <section class="card">
        <div class="section-header">
          <div>
            <h2>${escapeHtml(this.t("reports"))}</h2>
            <p>${escapeHtml(this.t("calendarStatus"))}: ${escapeHtml(this._stateValue(petId, "calendar_sync") || this.t("empty"))}</p>
          </div>
          <div class="actions inline">
            <button data-action="sync-calendar">${escapeHtml(this.t("syncCalendar"))}</button>
            <button data-action="generate-vet-txt">${escapeHtml(this.t("generateVetTxt"))}</button>
            <button data-action="generate-vet-pdf">${escapeHtml(this.t("generateVetPdf"))}</button>
            <button data-action="generate-ops-txt">${escapeHtml(this.t("generateOpsTxt"))}</button>
            <button data-action="generate-ops-pdf">${escapeHtml(this.t("generateOpsPdf"))}</button>
          </div>
        </div>
        <div class="two-col">
          <div>
            <h3>${escapeHtml(this.t("linkedCalendars"))}</h3>
            ${linkedCalendars.length ? `<ul class="list">${linkedCalendars.map((item) => `
              <li>
                <div>
                  <strong>${escapeHtml(item.calendar_entity_id || "calendar")}</strong>
                  <span>${escapeHtml(item.source_of_truth || "diva")}</span>
                </div>
              </li>`).join("")}</ul>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
            <h3>${escapeHtml(this.t("conflicts"))}</h3>
            <div class="stat">${escapeHtml(String(calendar.conflicts_count || 0))}</div>
          </div>
          <div>
            <h3>${escapeHtml(this.t("recentReports"))}</h3>
            ${reports.length ? `<ul class="list">${reports.slice().reverse().map((report) => `
              <li>
                <div>
                  <strong>${escapeHtml(report.kind || "report")}</strong>
                  <span>${escapeHtml(report.generated_at || "")}</span>
                </div>
                <code>${escapeHtml(report.path || report.report_path || "")}</code>
              </li>`).join("")}</ul>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
          </div>
        </div>
        <div class="subsection">
          <h3>${escapeHtml(this.t("conflicts"))}</h3>
          ${conflicts.length ? `<ul class="list">${conflicts.slice().reverse().map((item) => `
            <li>
              <div>
                <strong>${escapeHtml(this.t(`conflictTypes.${item.conflict_type}`) || item.reason || "conflict")}</strong>
                <span>${escapeHtml(item.occurred_at || "")}</span>
              </div>
              <span>${escapeHtml(item.reason || "")}</span>
              <code>${escapeHtml(`${item.calendar_entity_id || ""} • ${item.sync_key || ""}`)}</code>
              <div class="actions">
                <button data-action="open-calendar-conflict" data-conflict-id="${escapeHtml(item.conflict_id || "")}">${escapeHtml(this.t("reviewConflict"))}</button>
              </div>
            </li>`).join("")}</ul>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
        </div>
        <div class="subsection">
          <h3>${escapeHtml(this.t("journal"))}</h3>
          ${recentJournal.length ? `<ul class="list">${recentJournal.slice().reverse().slice(0, 10).map((item) => `
            <li>
              <div>
                <strong>${escapeHtml(item.action || "event")}</strong>
                <span>${escapeHtml(item.timestamp || "")}</span>
              </div>
              <span>${escapeHtml(item.note || "")}</span>
            </li>`).join("")}</ul>` : `<div class="empty">${escapeHtml(this.t("empty"))}</div>`}
        </div>
      </section>`;
  }

  _bindEvents() {
    const root = this.shadowRoot;
    if (!root) {
      return;
    }

    root.getElementById("pet-select")?.addEventListener("change", (event) => {
      this._selectedPetId = event.target.value;
      this._render();
    });
    root.querySelectorAll("[data-action='close-dialog']").forEach((node) => node.addEventListener("click", () => this._closeDialog()));
    root.getElementById("medication-form")?.addEventListener("submit", (event) => this._handleMedicationSubmit(event));
    root.getElementById("vaccine-override-form")?.addEventListener("submit", (event) => this._handleVaccineOverrideSubmit(event));
    root.getElementById("vaccine-reschedule-form")?.addEventListener("submit", (event) => this._handleRescheduleSubmit(event));
    root.getElementById("log-dose-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.target);
      await this._callService("log_medication_dose", {
        medication_name: form.get("medication_name"),
        dose: form.get("dose") || undefined,
        actor: form.get("actor") || undefined,
        note: form.get("note") || undefined,
      });
    });

    root.getElementById("refresh-view")?.addEventListener("click", () => this._render());
    root.querySelectorAll("button[data-action='open-medication-add']").forEach((node) => node.addEventListener("click", () => this._openDialog("medication")));
    root.querySelectorAll("button[data-action='open-vaccine-add']").forEach((node) => node.addEventListener("click", () => this._openDialog("vaccine_override")));
    root.querySelectorAll("button[data-action='sync-calendar']").forEach((node) => node.addEventListener("click", () => this._callService("sync_calendar", { days: 30 })));
    root.querySelectorAll("button[data-action='generate-vet-txt']").forEach((node) => node.addEventListener("click", () => this._callService("generate_vet_report", { report_format: "txt", history_days: 30 }, { closeDialog: false })));
    root.querySelectorAll("button[data-action='generate-vet-pdf']").forEach((node) => node.addEventListener("click", () => this._callService("generate_vet_report", { report_format: "pdf", history_days: 30 }, { closeDialog: false })));
    root.querySelectorAll("button[data-action='generate-ops-txt']").forEach((node) => node.addEventListener("click", () => this._callService("generate_operations_report", { report_format: "txt", history_days: 7 }, { closeDialog: false })));
    root.querySelectorAll("button[data-action='generate-ops-pdf']").forEach((node) => node.addEventListener("click", () => this._callService("generate_operations_report", { report_format: "pdf", history_days: 7 }, { closeDialog: false })));
    const conflicts = (this._sensorAttrs(this._selectedPetId, "calendar_conflicts").conflicts || []).slice().reverse();
    root.querySelectorAll("button[data-action='open-calendar-conflict']").forEach((node) => node.addEventListener("click", () => {
      const item = conflicts.find((entry) => entry.conflict_id === node.dataset.conflictId);
      if (item) {
        this._openDialog("calendar_conflict", item);
      }
    }));
    root.querySelectorAll("button[data-action='resolve-calendar-conflict']").forEach((node) => node.addEventListener("click", () => {
      const conflictId = this._dialog?.payload?.conflict_id;
      if (!conflictId) {
        return;
      }
      const resolution = node.dataset.resolution;
      this._callService(
        "resolve_calendar_conflict",
        { conflict_id: conflictId, resolution },
        { successMessage: this.t("statusConflictResolved") },
      );
    }));

    const courses = this._sensorAttrs(this._selectedPetId, "active_medications").configured_courses || [];
    root.querySelectorAll("button[data-action='edit-medication']").forEach((node) => node.addEventListener("click", () => {
      const item = courses[Number(node.dataset.index)];
      this._openDialog("medication", item);
    }));
    root.querySelectorAll("button[data-action='log-dose']").forEach((node) => node.addEventListener("click", () => {
      const item = courses[Number(node.dataset.index)];
      this._openDialog("log_dose", item);
    }));
    root.querySelectorAll("button[data-action='remove-medication']").forEach((node) => node.addEventListener("click", () => {
      const item = courses[Number(node.dataset.index)];
      this._openDialog("confirm", {
        message: this.t("confirmDeleteMedication"),
        onConfirm: () => this._callService("remove_medication_course", { medication_name: item.medication_name }),
      });
    }));

    const plan = this._sensorAttrs(this._selectedPetId, "vaccine_status").effective_plan || [];
    const overrides = this._sensorAttrs(this._selectedPetId, "vaccine_status").configured_overrides || [];
    root.querySelectorAll("button[data-action='complete-vaccine']").forEach((node) => node.addEventListener("click", () => {
      const item = plan[Number(node.dataset.index)];
      this._openDialog("confirm", {
        message: this.t("confirmCompleteVaccine"),
        onConfirm: () => this._callService("complete_vaccine_dose", { vaccine_dose_id: item.vaccine_dose_id, vaccine_name: item.vaccine_name }),
      });
    }));
    root.querySelectorAll("button[data-action='reschedule-vaccine']").forEach((node) => node.addEventListener("click", () => {
      const item = plan[Number(node.dataset.index)];
      this._openDialog("reschedule_vaccine", item);
    }));
    root.querySelectorAll("button[data-action='cancel-vaccine']").forEach((node) => node.addEventListener("click", () => {
      const item = plan[Number(node.dataset.index)];
      this._openDialog("confirm", {
        message: this.t("confirmCancelVaccine"),
        onConfirm: () => this._callService("cancel_vaccine", { vaccine_dose_id: item.vaccine_dose_id, vaccine_name: item.vaccine_name }),
      });
    }));
    root.querySelectorAll("button[data-action='edit-vaccine-override']").forEach((node) => node.addEventListener("click", () => {
      const item = plan[Number(node.dataset.index)];
      this._openDialog("vaccine_override", item);
    }));
    root.querySelectorAll("button[data-action='edit-configured-override']").forEach((node) => node.addEventListener("click", () => {
      const item = overrides[Number(node.dataset.index)];
      this._openDialog("vaccine_override", item);
    }));
    root.querySelectorAll("button[data-action='remove-vaccine-override']").forEach((node) => node.addEventListener("click", () => {
      const item = overrides[Number(node.dataset.index)];
      this._openDialog("confirm", {
        message: this.t("confirmRemoveOverride"),
        onConfirm: () => this._callService("remove_vaccine_override", {
          vaccine_dose_id: item.vaccine_dose_id || undefined,
          vaccine_name: item.vaccine_name || undefined,
        }),
      });
    }));

    root.querySelector("button[data-action='confirm-dialog']")?.addEventListener("click", async () => {
      const callback = this._dialog?.payload?.onConfirm;
      if (callback) {
        await callback();
      }
    });
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }
    const pets = this._collectPets();
    const pet = this._selectedPet();
    const statusHtml = this._status ? `<div class="status ${escapeHtml(this._status.level)}">${escapeHtml(this._status.message)}</div>` : "";
    const petOptions = pets.map((item) => `<option value="${escapeHtml(item.pet_id)}" ${item.pet_id === this._selectedPetId ? "selected" : ""}>${escapeHtml(item.pet_name)}</option>`).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          min-height: 100%;
          background: var(--lovelace-background, var(--primary-background-color));
          color: var(--primary-text-color);
          font-family: var(--paper-font-body1_-_font-family, system-ui, sans-serif);
        }
        .page {
          padding: 24px;
          max-width: 1440px;
          margin: 0 auto;
        }
        .hero {
          display: flex;
          justify-content: space-between;
          gap: 16px;
          align-items: flex-start;
          margin-bottom: 24px;
          padding: 24px;
          border-radius: 24px;
          background: linear-gradient(135deg, rgba(214, 120, 55, 0.18), rgba(53, 90, 122, 0.18));
          border: 1px solid var(--divider-color);
        }
        .hero h1 { margin: 0 0 8px; font-size: 32px; }
        .hero p { margin: 0; color: var(--secondary-text-color); max-width: 760px; }
        .toolbar {
          display: flex;
          gap: 12px;
          align-items: center;
          flex-wrap: wrap;
        }
        select, input, textarea, button {
          font: inherit;
        }
        select, input, textarea {
          width: 100%;
          box-sizing: border-box;
          padding: 10px 12px;
          border-radius: 12px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
        }
        button {
          border: 0;
          border-radius: 12px;
          padding: 10px 14px;
          background: var(--primary-color);
          color: var(--text-primary-color, white);
          cursor: pointer;
        }
        button.secondary {
          background: transparent;
          color: var(--primary-text-color);
          border: 1px solid var(--divider-color);
        }
        button.danger {
          background: #9f3a2d;
          color: white;
        }
        button:disabled {
          opacity: 0.6;
          cursor: wait;
        }
        .status {
          margin-bottom: 16px;
          padding: 12px 14px;
          border-radius: 14px;
          border: 1px solid var(--divider-color);
        }
        .status.success { background: rgba(61, 139, 88, 0.12); }
        .status.error { background: rgba(159, 58, 45, 0.16); }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
          gap: 16px;
        }
        .card {
          background: var(--card-background-color);
          border-radius: 20px;
          padding: 18px;
          border: 1px solid var(--divider-color);
          box-shadow: var(--ha-card-box-shadow, none);
        }
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 14px;
        }
        .section-header h2, .subsection h3 {
          margin: 0 0 6px;
        }
        .section-header p, .subsection p, .hint {
          margin: 0;
          color: var(--secondary-text-color);
          font-size: 14px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }
        th, td {
          padding: 10px 8px;
          border-bottom: 1px solid var(--divider-color);
          vertical-align: top;
          text-align: left;
        }
        .actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          justify-content: flex-end;
        }
        .actions.inline {
          justify-content: flex-start;
        }
        .list {
          list-style: none;
          padding: 0;
          margin: 0;
          display: grid;
          gap: 10px;
        }
        .list li {
          padding: 12px;
          border-radius: 14px;
          background: rgba(127, 127, 127, 0.08);
          display: grid;
          gap: 8px;
        }
        .list li > div {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: center;
        }
        .empty {
          color: var(--secondary-text-color);
          padding: 18px 0 4px;
        }
        .subsection {
          margin-top: 18px;
        }
        .two-col {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 16px;
        }
        .stat {
          font-size: 42px;
          font-weight: 700;
          margin-top: 8px;
        }
        .dialog-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(16, 18, 24, 0.56);
          display: grid;
          place-items: center;
          z-index: 1000;
          padding: 24px;
        }
        .dialog {
          width: min(540px, 100%);
          background: var(--card-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 24px;
          padding: 20px;
          box-shadow: 0 28px 60px rgba(0, 0, 0, 0.25);
        }
        .dialog.compact {
          width: min(420px, 100%);
        }
        .dialog h3 {
          margin: 0 0 16px;
        }
        .dialog-form {
          display: grid;
          gap: 12px;
        }
        .dialog-form label {
          display: grid;
          gap: 6px;
          font-size: 14px;
        }
        .dialog-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 8px;
        }
        code {
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          word-break: break-all;
          background: rgba(127, 127, 127, 0.08);
          padding: 4px 6px;
          border-radius: 8px;
        }
        @media (max-width: 900px) {
          .page { padding: 16px; }
          .hero { flex-direction: column; }
          .grid { grid-template-columns: 1fr; }
        }
      </style>
      <div class="page">
        ${statusHtml}
        <section class="hero">
          <div>
            <h1>${escapeHtml(this.t("title"))}</h1>
            <p>${escapeHtml(this.t("subtitle"))}</p>
          </div>
          <div class="toolbar">
            <label>
              <span>${escapeHtml(this.t("pet"))}</span>
              <select id="pet-select" ${pets.length ? "" : "disabled"}>${petOptions}</select>
            </label>
            <button id="refresh-view" class="secondary">${escapeHtml(this.t("refresh"))}</button>
          </div>
        </section>
        ${this._busy ? `<div class="status">${escapeHtml(this.t("working"))}</div>` : ""}
        ${pet ? `
          <div class="grid">
            ${this._renderMedicationSection(pet.pet_id)}
            ${this._renderVaccineSection(pet.pet_id)}
            ${this._renderReportsSection(pet.pet_id)}
          </div>` : `<div class="card empty">${escapeHtml(this.t("noPets"))}</div>`}
      </div>
      ${this._renderDialog()}`;

    this._bindEvents();
  }
}

if (!customElements.get("diva-editor-panel")) {
  customElements.define("diva-editor-panel", DivaEditorPanel);
}
