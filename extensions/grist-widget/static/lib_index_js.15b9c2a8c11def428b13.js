"use strict";
(self["webpackChunkgrist_widget"] = self["webpackChunkgrist_widget"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var comlink__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! comlink */ "webpack/sharing/consume/default/comlink/comlink");
/* harmony import */ var comlink__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(comlink__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _initKernelPy__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./initKernelPy */ "./lib/initKernelPy.js");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__);



const pendingWorkers = [];
class MyWorker extends Worker {
    constructor(scriptURL, options) {
        super(scriptURL, options);
        const { grist } = window;
        if (grist) {
            exposeWorker(this, grist);
        }
        else {
            pendingWorkers.push(this);
        }
    }
}
window.Worker = MyWorker;
const emptyNotebook = {
    content: {
        'metadata': {
            'language_info': {
                'codemirror_mode': {
                    'name': 'python',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.11'
            },
            'kernelspec': {
                'name': 'python',
                'display_name': 'Python (Pyodide)',
                'language': 'python'
            }
        },
        'nbformat_minor': 4,
        'nbformat': 4,
        'cells': [
            {
                'cell_type': 'code',
                'source': '',
                'metadata': {},
                'execution_count': null,
                'outputs': []
            }
        ]
    },
    format: 'json',
};
let currentRecord = null;
/**
 * Initialization data for the grist-widget extension.
 */
const plugin = {
    id: 'grist-widget:plugin',
    description: 'Custom Grist widget for a JupyterLite notebook',
    autoStart: true,
    requires: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__.IFileBrowserCommands],
    activate: (app) => {
        hideBars(app).catch(e => console.error(e));
        const script = document.createElement('script');
        script.src = 'https://docs.getgrist.com/grist-plugin-api.js';
        script.id = 'grist-plugin-api';
        script.addEventListener('load', async () => {
            const grist = window.grist;
            app.serviceManager.contents.fileChanged.connect(async (_, change) => {
                var _a;
                if (change.type === 'save' && ((_a = change.newValue) === null || _a === void 0 ? void 0 : _a.path) === 'notebook.ipynb') {
                    const withoutOutputs = {
                        ...change.newValue,
                        content: {
                            ...change.newValue.content,
                            cells: change.newValue.content.cells.map((cell) => ({
                                ...cell,
                                outputs: 'outputs' in cell ? [] : undefined,
                            })),
                        },
                    };
                    grist.setOption('notebook', withoutOutputs);
                }
            });
            grist.onRecord((record) => {
                currentRecord = record;
            });
            grist.ready();
            const notebook = await grist.getOption('notebook') || emptyNotebook;
            await app.serviceManager.contents.save('notebook.ipynb', notebook);
            await app.commands.execute('filebrowser:open-path', { path: 'notebook.ipynb' });
            console.log('JupyterLab extension grist-widget is activated!');
            const kernel = await getKernel(app);
            kernel.requestExecute({ code: (0,_initKernelPy__WEBPACK_IMPORTED_MODULE_2__["default"])() });
            for (const worker of pendingWorkers) {
                exposeWorker(worker, grist);
            }
            await app.commands.execute('notebook:run-all-cells');
        });
        document.head.appendChild(script);
    }
};
async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
function exposeWorker(worker, grist) {
    comlink__WEBPACK_IMPORTED_MODULE_0__.expose({
        grist: {
            ...grist,
            getTable: (tableId) => comlink__WEBPACK_IMPORTED_MODULE_0__.proxy(grist.getTable(tableId)),
            getCurrentRecord: () => currentRecord,
        }
    }, worker);
}
async function getKernel(app) {
    var _a, _b, _c;
    while (true) {
        const widget = app.shell.currentWidget;
        const kernel = (_c = (_b = (_a = widget === null || widget === void 0 ? void 0 : widget.context) === null || _a === void 0 ? void 0 : _a.sessionContext) === null || _b === void 0 ? void 0 : _b.session) === null || _c === void 0 ? void 0 : _c.kernel;
        if (kernel) {
            return kernel;
        }
        await delay(100);
    }
}
async function hideBars(app) {
    while (!app.shell.currentWidget) {
        await delay(100);
    }
    const shell = app.shell;
    shell.collapseLeft();
    shell._titleHandler.parent.setHidden(true);
    shell._leftHandler.sideBar.setHidden(true);
    for (let i = 0; i < 1000; i++) {
        if (!shell.leftCollapsed) {
            shell.collapseLeft();
            shell._leftHandler.sideBar.setHidden(true);
            break;
        }
        else {
            await delay(10);
        }
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/initKernelPy.js":
/*!*****************************!*\
  !*** ./lib/initKernelPy.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
function code() {
    const packageUrl = new URL('../files/package.tar.gz', window.location.href).href;
    // language=Python
    return `
async def __bootstrap_grist(url):
    from pyodide.http import pyfetch  # noqa
    import io
    import tarfile
    
    response = await pyfetch(url)
    bytes_file = io.BytesIO(await response.bytes())
    with tarfile.open(fileobj=bytes_file) as tar:
        tar.extractall()
    
    import grist.browser  # noqa
    return grist.browser.grist

grist = await __bootstrap_grist(${JSON.stringify(packageUrl)})
`;
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (code);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.15b9c2a8c11def428b13.js.map