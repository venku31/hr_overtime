// frappe.ui.form.on('Timesheet', {
//     validate(frm){
//         //code here
//         if(frm.doc.total_hours){
//             if(parseInt(frm.doc.total_hours) > 9){
//                 var overtime = parseInt(frm.doc.total_hours) - 9
//                 frm.set_value("overtime_hours", overtime)
//                 frm.refresh_field("overtime_hours")
//             }
//         }
//     },
   

// })

//  frappe.ui.form.on('Timesheet',  {
//     validate(frm){
// 		// if(frm.doc.total_hours>0){
// 	frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet").then( max_working_hours_against_timesheet=>{
//         cur_frm.set_value('overtime_hours', max_working_hours_against_timesheet);
//     });
//         //     if(parseInt(frm.doc.total_hours) > parseInt(max_working_hours)){
//         //         var overtime = parseInt(frm.doc.total_hours) - parseInt(max_working_hours)
//         //         cur_frm.set_value("overtime_hours", 5)
//         //         frm.refresh_field("overtime_hours")
//         //     }
//         // }
//         frappe.db.get_single_value('Payroll Settings', 'add_rate').then( add_rate=>{
//             cur_frm.set_value('add_rate', add_rate);
//         });
//         // cur_frm.set_value('overtime_hours', frm.doc.total_hours-frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet"));
// 	}
// })