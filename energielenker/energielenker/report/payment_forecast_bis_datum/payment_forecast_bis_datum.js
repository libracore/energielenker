// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Forecast bis Datum"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label": __("Zahlungsdatum von einschl."),
            "fieldtype": "Date"
        },
        {
            "fieldname":"date",
            "label": __("Zahlungsdatum bis einschl."),
            "fieldtype": "Date",
            "default": frappe.datetime.year_end(),
            "reqd": 1
        },
        {
            "fieldname":"ausfuehrung",
            "label": __("Ausführung"),
            "fieldtype": "Select",
            "options": 'Auftrag\nKostenstelle',
            "default": "Auftrag"
        }
    ],
    onload: function(report) {
        load_script("assets/energielenker/js/xlsx.full.min.js");
        report.page.add_inner_button(__("Exportieren"), function() {
            create_excel_with_hyperlinks(report);
        });
    }
};

function load_script(url) {
    const script = document.createElement('script');
    script.src = url;
    script.type = 'text/javascript';
    document.head.appendChild(script);
    script.onload = () => {
        console.log(`Script ${url} loaded successfully.`);
    };
}

function create_excel_with_hyperlinks(report) {

    var columns = report.columns;
    var data = report.data;

    // Neues Workbook erstellen
    const wb = XLSX.utils.book_new();

    // Daten für das Worksheet vorbereiten
    const report_data = [];

    const report_header = columns.map(col => col.label);
    report_data.push(report_header);

    data.forEach(row => {
        const row_data = columns.map(col => row[col.fieldname]);
        report_data.push(row_data);
    });

    // Worksheet erstellen
    const ws = XLSX.utils.aoa_to_sheet(report_data);

    // Hyperlinks zu den entsprechenden Zellen hinzufügen
    for (let i = 1; i < report_data.length; i++) {
        const cell_address = 'B' + (i + 1);
        const cell_value = report_data[i][1];
        if (cell_value) {
            ws[cell_address].l = { Target: cell_value, Tooltip: 'Zahlungsplan' };
            ws[cell_address].s = { font: { color: { rgb: "0000FF" }, underline: true } }; // Blau und unterstrichen
            ws[cell_address].v = 'Zahlungsplan';
        }
    }

    // Spaltenbreite setzen für bessere Darstellung
    ws['!cols'] = [
        { wch: 15 },  // Spalte A
        { wch: 15 },  // Spalte B
        { wch: 15 },  // Spalte C
        { wch: 15 },  // Spalte D
        { wch: 40 },  // Spalte E
        { wch: 15 },  // Spalte F
        { wch: 20 },  // Spalte G
        { wch: 15 },  // Spalte H
        { wch: 15 },  // Spalte I
        { wch: 30 }   // Spalte J
    ];

    // Header-Zeile formatieren (fett)
    for (let i = 1; i <= 10; i++) {
        const cell_address = String.fromCharCode(64 + i) + '1'; // A1, B1, ..., J1
        if (!ws[cell_address]) continue; // Sicherstellen, dass die Zelle existiert
        ws[cell_address].s = { font: { bold: true } }; // Fettdruck
    }

    // Worksheet zum Workbook hinzufügen
    XLSX.utils.book_append_sheet(wb, ws, "Payment Forecast bis Datum");

    // Excel-Datei generieren und herunterladen
    const fileName = 'Payment_Forecast_bis_Datum.xlsx';
    XLSX.writeFile(wb, fileName);

}
