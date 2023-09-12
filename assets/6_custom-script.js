// https://stackoverflow.com/questions/68337654/adding-javascript-to-my-plotly-dash-app-python
// alert('If you see this alert, then your custom JavaScript script has run!')


/**
 *
 * @param {string} id
 * @param {*} event
 * @param {(this: HTMLElement, ev: any) => any} callback
 * @param {boolean | AddEventListenerOptions} options
 */
function attachEventToDash(id, event, callback, options) {
    debugger;
    var observer = new MutationObserver(function (_mutations, obs) {
        var ele = document.getElementById(id);
        if (ele) {
            debugger;
            ele.addEventListener(event, callback, options)
            obs.disconnect();
        }
    });
    window.addEventListener('DOMContentLoaded', function () {
        observer.observe(document, {
            childList: true,
            subtree: true
        });
    })
  }
  