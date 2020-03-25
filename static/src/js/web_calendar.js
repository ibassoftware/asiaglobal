// Copyright (C) 2018 by Camptocamp
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define('asiaglobal.CalendarQuickCreate', function (require) {
    'use strict';

    var quickCreate = require('web.CalendarQuickCreate');
    var rpc = require('web.rpc');

    quickCreate.include({
        /**
         * Gathers data from the quick create dialog a launch quick_create(data) method
         */
        _quickAdd: function (dataCalendar) {
            dataCalendar = $.extend({}, this.dataTemplate, dataCalendar);
            var val = this.$('input').val().trim();
            var type = this.$('#type').val().trim();
            var partner_id = parseInt(this.$('#partner_id option:selected').val());
            var project_id = parseInt(this.$('#project_id option:selected').val());
            dataCalendar.title = val;
            dataCalendar.type = type;
            dataCalendar.partner_id = partner_id;
            dataCalendar.project_id = project_id;
            return (val)? this.trigger_up('quickCreate', {data: dataCalendar, options: this.options}) : false;
        },

        renderElement: function(){
            var self = this;

            this._super();

            this.$('#partner_id_section').hide();
            this.$('#project_id_section').hide();

            this.$('#type').click(function(event){
                var type = self.$('#type').val();
                // console.log(type);
                if(type != 'existing'){
                    self.$('#partner_id_section').hide();
                    self.$('#project_id_section').hide();
                }
                else {
                    self.$('#partner_id_section').show();
                    self.$('#project_id_section').show();
                }
            });

            this.$('#partner_id').click(function(event){
                var partner_id = parseInt(self.$('#partner_id option:selected').val());
                // console.log(partner_id);
                if(!isNaN(partner_id)){
                    var domain = [['partner_id','=',partner_id]];
                    // console.log(domain);
                    rpc.query({
                        model: 'sale.order',
                        method: 'search_read',
                        args: [domain, ['id','name','partner_id']],
                    })
                    .then(function(projects){
                        self.$('#project_id option').remove();
                        self.$('#project_id').append($('<option/>').text('Select Project List'));
                        _.each(projects, function (project) {
                            self.$('#project_id').append($('<option/>').attr('value',project.id).text(project.name));
                        });
                    });
                }

            });

        },

        show: function(){ this.$el.removeClass('oe_hidden'); },
        hide: function(){ this.$el.addClass('oe_hidden'); },
       
    });

});

odoo.define('asiaglobal.CalendarModel', function (require) {
    'use strict';

    var calendarModel = require('web.CalendarModel');
    var rpc = require('web.rpc');

    calendarModel.include({
        
        /**
        * Transform fullcalendar event object to OpenERP Data object
        */
        calendarEventToRecord: function (event) {
            // Normalize event_end without changing fullcalendars event.
            var data = {'name': event.title, 'type': event.type, 'partner_id': event.partner_id, 'project_id': event.project_id};
            var start = event.start.clone();
            var end = event.end && event.end.clone();

            // Detects allDay events (86400000 = 1 day in ms)
            if (event.allDay || (end && end.diff(start) % 86400000 === 0)) {
                event.allDay = true;
            }

            // Set end date if not existing
            if (!end || end.diff(start) < 0) { // undefined or invalid end date
                if (event.allDay) {
                    end = start.clone();
                } else {
                    // in week mode or day mode, convert allday event to event
                    end = start.clone().add(2, 'h');
                }
            } else if (event.allDay) {
                // For an "allDay", FullCalendar gives the end day as the
                // next day at midnight (instead of 23h59).
                end.add(-1, 'days');
            }

            // An "allDay" event without the "all_day" option is not considered
            // as a 24h day. It's just a part of the day (by default: 7h-19h).
            if (event.allDay) {
                if (!this.mapping.all_day) {
                    if (event.r_start) {
                        start.hours(event.r_start.hours())
                             .minutes(event.r_start.minutes())
                             .seconds(event.r_start.seconds())
                             .utc();
                        end.hours(event.r_end.hours())
                           .minutes(event.r_end.minutes())
                           .seconds(event.r_end.seconds())
                           .utc();
                    } else {
                        // default hours in the user's timezone
                        start.hours(7).add(-this.getSession().getTZOffset(start), 'minutes');
                        end.hours(19).add(-this.getSession().getTZOffset(end), 'minutes');
                    }
                }
            } else {
                start.add(-this.getSession().getTZOffset(start), 'minutes');
                end.add(-this.getSession().getTZOffset(end), 'minutes');
            }

            if (this.mapping.all_day) {
                if (event.record) {
                    data[this.mapping.all_day] =
                        (this.scale !== 'month' && event.allDay) ||
                        event.record[this.mapping.all_day] &&
                        end.diff(start) < 10 ||
                        false;
                } else {
                    data[this.mapping.all_day] = event.allDay;
                }
            }

            data[this.mapping.date_start] = start;
            if (this.mapping.date_stop) {
                data[this.mapping.date_stop] = end;
            }

            if (this.mapping.date_delay) {
                data[this.mapping.date_delay] = (end.diff(start) <= 0 ? end.endOf('day').diff(start) : end.diff(start)) / 1000 / 3600;
            }

            return data;
        },

        
       
    });

});

odoo.define('asiaglobal.CalendarController', function (require) {
    'use strict';

    var calendarController = require('web.CalendarController');
    var QuickCreate = require('web.CalendarQuickCreate');
    var dialogs = require('web.view_dialogs');
    var Dialog = require('web.Dialog');
    var core = require('web.core');

    var _t = core._t;
    var QWeb = core.qweb;

    var rpc = require('web.rpc');
    var session = require('web.session');

    calendarController.include({
        /**
         * @override
         * @param {Widget} parent
         * @param {AbstractModel} model
         * @param {AbstractRenderer} renderer
         * @param {Object} params
        */
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.current_start = null;
            this.displayName = params.displayName;
            this.quickAddPop = params.quickAddPop;
            this.disableQuickCreate = params.disableQuickCreate;
            this.eventOpenPopup = params.eventOpenPopup;
            this.formViewId = params.formViewId;
            this.readonlyFormViewId = params.readonlyFormViewId;
            this.mapping = params.mapping;
            this.context = params.context;
            // The quickCreating attribute ensures that we don't do several create
            this.quickCreating = false;

            // RCS: Fill Partner and Project list
            this.partners = [];
            this.projects = [];
            this._get_partners();
            // this._get_projects();
        },

        /**
         * Handles saving data coming from quick create box
         *
         * @private
         * @param {OdooEvent} event
        */
        _onQuickCreate: function (event) {
            var self = this;
            if (this.quickCreating) {
                return;
            }
            
            this.quickCreating = true;

            var type = event.data.data.type;
            var context = _.extend({}, this.context, event.options && event.options.context);
            
            var start_date = event.data.data.start || null;
            var deadline = start_date.clone().add(7, 'days');

            // console.log('TEST');
            // console.log(type);

            if (type === 'new') {
                context.default_name = event.data.data.title || null;
                var options = _.extend({}, this.options, event.options, {context: context});
                
                // this.create_lead(event, context, options)
                //     .then(function () {
                //         self.quick.destroy();
                //         self.quick = null;
                //         self.reload();
                //     });

                new dialogs.FormViewDialog(self, {
                    res_model: 'crm.lead',
                    context: context,
                    title: 'Create: Prospects',
                    disable_multiple_selection: true,
                    on_saved: function (lead_id) {
                        if (event.data.on_save) {
                            event.data.on_save();
                        }

                        // Create activity (model, record_id, description, deadline)
                        self._create_activity('crm.lead', lead_id.data.id, lead_id.data.name, deadline);

                        self.model.createRecord(event)
                            .then(function () {
                                self.quick.destroy();
                                self.quick = null;
                                self.reload();
                            })
                            .fail(function (error, errorEvent) {
                                // This will occurs if there are some more fields required
                                // Preventdefaulting the error event will prevent the traceback window
                                errorEvent.preventDefault();
                                event.data.options.disableQuickCreate = true;
                                event.data.data.on_save = self.quick.destroy.bind(self.quick);
                                self._onOpenCreate(event.data);
                            })
                            .always(function () {
                                self.quickCreating = false;
                            });

                    },
                }).open();

            } 

            else if (type === 'existing') {
                var partner_id = parseInt(self.$('#partner_id option:selected').val());
                // console.log(partner_id);
                // console.log(QuickCreate);
                // var project_id = parseInt(self.$('#project_id option:selected').val());
                var project_id = event.data.data.project_id || null;
                var model = 'sale.order';
                var domain = [['model','=',model]];
                // console.log('EXISTING!');
                // console.log(project_id);

                new dialogs.FormViewDialog(self, {
                    res_model: model,
                    res_id: project_id,
                    context: context,
                    title: 'Edit: Project List',
                    disable_multiple_selection: true,
                    on_saved: function (project) {
                        if (event.data.on_save) {
                            event.data.on_save();
                        }

                        // Create activity (model, record_id, description, deadline)
                        self._create_activity(model, project.data.id, project.data.name, deadline);

                        self.model.createRecord(event)
                            .then(function () {
                                self.quick.destroy();
                                self.quick = null;
                                self.reload();
                            })
                            .fail(function (error, errorEvent) {
                                // This will occurs if there are some more fields required
                                // Preventdefaulting the error event will prevent the traceback window
                                errorEvent.preventDefault();
                                event.data.options.disableQuickCreate = true;
                                event.data.data.on_save = self.quick.destroy.bind(self.quick);
                                self._onOpenCreate(event.data);
                            })
                            .always(function () {
                                self.quickCreating = false;
                            });

                    },
                }).open();

            } 

            else {
                context.default_name = event.data.data.title || null;
                this.model.createRecord(event)
                    .then(function () {
                        self.quick.destroy();
                        self.quick = null;
                        self.reload();
                    })
                    .fail(function (error, errorEvent) {
                        // This will occurs if there are some more fields required
                        // Preventdefaulting the error event will prevent the traceback window
                        errorEvent.preventDefault();
                        event.data.options.disableQuickCreate = true;
                        event.data.data.on_save = self.quick.destroy.bind(self.quick);
                        self._onOpenCreate(event.data);
                    })
                    .always(function () {
                        self.quickCreating = false;
                    });
            }
            
        },

        /**
         * @param {OdooEvent} event
        */
        _onOpenCreate: function (event) {
            var self = this;
            if (this.model.get().scale === "month") {
                event.data.allDay = true;
            }
            
            event.data.partner_id = self.partners;
            event.data.project_id = self.projects;
            
            var data = this.model.calendarEventToRecord(event.data);

            var context = _.extend({}, this.context, event.options && event.options.context);
            context.default_name = data.name || null;
            context['default_' + this.mapping.date_start] = data[this.mapping.date_start] || null;
            if (this.mapping.date_stop) {
                context['default_' + this.mapping.date_stop] = data[this.mapping.date_stop] || null;
            }
            if (this.mapping.date_delay) {
                context['default_' + this.mapping.date_delay] = data[this.mapping.date_delay] || null;
            }
            if (this.mapping.all_day) {
                context['default_' + this.mapping.all_day] = data[this.mapping.all_day] || null;
            }

            for (var k in context) {
                if (context[k] && context[k]._isAMomentObject) {
                    context[k] = context[k].clone().utc().format('YYYY-MM-DD HH:mm:ss');
                }
            }

            var options = _.extend({}, this.options, event.options, {context: context});

            if (this.quick != null) {
                this.quick.destroy();
                this.quick = null;
            }

            if(!options.disableQuickCreate && !event.data.disableQuickCreate && this.quickAddPop) {
                this.quick = new QuickCreate(this, true, options, data, event.data);
                this.quick.open();
                this.quick.focus();
                return;
            }

            var title = _t("Create");
            if (this.renderer.arch.attrs.string) {
                title += ': ' + this.renderer.arch.attrs.string;
            }
            if (this.eventOpenPopup) {
                new dialogs.FormViewDialog(self, {
                    res_model: this.modelName,
                    context: context,
                    title: title,
                    disable_multiple_selection: true,
                    on_saved: function () {
                        if (event.data.on_save) {
                            event.data.on_save();
                        }
                        self.reload();
                    },
                }).open();
            } else {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: this.modelName,
                    views: [[this.formViewId || false, 'form']],
                    target: 'current',
                    context: context,
                });
            }
        },

        _get_partners: function () {
            var self = this;
            var domain = [['customer','=',true]];
            rpc.query({
                model: 'res.partner',
                method: 'search_read',
                args: [domain, ['id','name','customer']],
            })
            .then(function(partners){
                // console.log("YEAH");
                // console.log(partners);
                self.partners = partners;
            });
        },

        _get_projects: function () {
            var self = this;
            // var domain = [['customer','=',true]];
            rpc.query({
                model: 'sale.order',
                method: 'search_read',
                args: [[], ['id','name']],
            })
            .then(function(projects){
                // console.log("YEAH2");
                // console.log(projects);
                self.projects = projects;
            });
        },

        create_lead: function (event, context, options) {
            var self = this;
            var start_date = event.data.data.start || null;
            var deadline = start_date.clone().add(7, 'days');
            new dialogs.FormViewDialog(self, {
                res_model: 'crm.lead',
                context: context,
                title: 'Create: Prospects',
                disable_multiple_selection: true,
                on_saved: function (lead_id) {
                    if (event.data.on_save) {
                        event.data.on_save();
                    }

                    // Create activity (model, record_id, description, deadline)
                    self._create_activity('crm.lead', lead_id.data.id, lead_id.data.name, deadline);

                    self.model.createRecord(event)
                        .then(function () {
                            self.quick.destroy();
                            self.quick = null;
                            self.reload();
                        })
                        .fail(function (error, errorEvent) {
                            // This will occurs if there are some more fields required
                            // Preventdefaulting the error event will prevent the traceback window
                            errorEvent.preventDefault();
                            event.data.options.disableQuickCreate = true;
                            event.data.data.on_save = self.quick.destroy.bind(self.quick);
                            self._onOpenCreate(event.data);
                        })
                        .always(function () {
                            self.quickCreating = false;
                        });

                },
            }).open();
        },

        _create_activity: function (model, record_id, description, deadline) {
            var self = this;
            var domain = [['model','=',model]];
            
            rpc.query({
                model: 'ir.model',
                method: 'search_read',
                args: [domain, ['id','model','name']],
            })
            .then(function(model_id){
                var args = {
                    'activity_type_id': 4,
                    'res_id': record_id,
                    'res_model_id': model_id[0].id,
                    'date_deadline': deadline,
                    'user_id': session.uid,
                    'note': description,
                    'summary':description
                };

                rpc.query({
                    model: 'mail.activity',
                    method: 'create',
                    args: [args],
                })
                // .then(function(activity_id){
                //     console.log("YEADYEAH");
                // });

            });
            
        },
       
    });

});