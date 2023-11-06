import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import * as Comlink from 'comlink';
import initKernelPy from './initKernelPy';
import { IFileBrowserCommands } from '@jupyterlab/filebrowser';

const pendingWorkers: MyWorker[] = [];

class MyWorker extends Worker {
  constructor(scriptURL: string | URL, options?: WorkerOptions) {
    super(scriptURL, options);
    const { grist } = (window as any);
    if (grist) {
      exposeWorker(this, grist);
    } else {
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
  format: 'json' as const,
};

let currentRecord: any = null;

/**
 * Initialization data for the grist-widget extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'grist-widget:plugin',
  description: 'Custom Grist widget for a JupyterLite notebook',
  autoStart: true,
  requires: [IFileBrowserCommands],
  activate: (app: JupyterFrontEnd) => {
    hideBars(app).catch(e => console.error(e));

    const script = document.createElement('script');
    script.src = 'https://docs.getgrist.com/grist-plugin-api.js';
    script.id = 'grist-plugin-api';
    script.addEventListener('load', async () => {
      const grist = (window as any).grist;

      app.serviceManager.contents.fileChanged.connect(async (_, change) => {
        if (change.type === 'save' && change.newValue?.path === 'notebook.ipynb') {
          const withoutOutputs = {
            ...change.newValue,
            content: {
              ...change.newValue.content,
              cells: change.newValue.content.cells.map((cell: any) => ({
                ...cell,
                outputs: 'outputs' in cell ? [] : undefined,
              })),
            },
          };
          grist.setOption('notebook', withoutOutputs);
        }
      });

      grist.onRecord((record: any) => {
        currentRecord = record;
      });

      grist.ready();

      const notebook = await grist.getOption('notebook') || emptyNotebook;
      await app.serviceManager.contents.save('notebook.ipynb', notebook);
      await app.commands.execute('filebrowser:open-path', { path: 'notebook.ipynb' });

      console.log('JupyterLab extension grist-widget is activated!');

      const kernel = await getKernel(app);
      kernel.requestExecute({ code: initKernelPy() });

      for (const worker of pendingWorkers) {
        exposeWorker(worker, grist);
      }

      await app.commands.execute('notebook:run-all-cells');
    });
    document.head.appendChild(script);
  }
};

async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function exposeWorker(worker: Worker, grist: any) {
  Comlink.expose({
    grist: {
      ...grist,
      getTable: (tableId: string) => Comlink.proxy(grist.getTable(tableId)),
      getCurrentRecord: () => currentRecord,
    }
  }, worker);
}

async function getKernel(app: JupyterFrontEnd) {
  while (true) {
    const widget = app.shell.currentWidget;
    const kernel = (widget as any)?.context?.sessionContext?.session?.kernel;
    if (kernel) {
      return kernel;
    }
    await delay(100);
  }
}

async function hideBars(app: JupyterFrontEnd) {
  while (!app.shell.currentWidget) {
    await delay(100);
  }
  const shell = app.shell as any;
  shell.collapseLeft();
  shell._titleHandler.parent.setHidden(true);
  shell._leftHandler.sideBar.setHidden(true);
  for (let i = 0; i < 1000; i++) {
    if (!shell.leftCollapsed) {
      shell.collapseLeft();
      shell._leftHandler.sideBar.setHidden(true);
      break;
    } else {
      await delay(10);
    }
  }
}

export default plugin;
