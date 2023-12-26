# JupyterLite Notebook Grist Custom Widget

See [USAGE.md](./USAGE.md) for instructions on how to use this widget in Grist. This README is for developers.

This repo is a custom deployment of JupyterLite generated from https://github.com/jupyterlite/demo.

## Development

1. Create and activate a virtual environment
2. `pip install -r requirements.txt`
3. In the `extension` folder, run `jlpm install`, then `jlpm build`, then `jlpm watch`. `jlpm` is a pinned version of `yarn` that is installed with JupyterLab, so you can use `yarn` or `npm` instead. `jlpm watch` will rebuild the extension when changes are made to the code under `extension/src`. For some reason it doesn't work without running `jlpm build` first at least once.
4. In a new tab, back in the repo root, activate the virtual environment again, then run `./dev.sh`. This will start a local server at http://localhost:8000 which you can use as a custom widget URL.
5. Make some changes to the code under `grist` or `extension/src`. Changing `.ts` files will rebuild the JS, but either way you still have to interrupt the server with Ctrl+C, rerun `.dev.sh`, and refresh the page to see the changes.
6. If you're having trouble, try various permutations of these commands:
   - `pip uninstall grist_jupyterlab_widget` (that's the Python package name of the `extension` folder)
   - `pip install -e extension`
   - `jupyter labextension develop ./extension` (part of `dev.sh`), maybe with the `--overwrite` flag.
   - `jlpm build` and `jlpm watch` within the `extension` folder

## Deployment

In the [grist-widget](https://github.com/gristlabs/grist-widget) repo, the `jupyterlite` folder is a git submodule pointing at a commit in the `gh-pages` branch of this repo. To fully deploy changes here to production for use in Grist, you need to:

0. Run `npm install` in the root of this repo.
1. Commit and push changes to this repo. It doesn't have to be in the main branch, but an actual commit is important for reference.
2. Run `npm run deploy` to build and push to the `gh-pages` branch. The commit message will contain the commit hash of the commit in step 1. You can use https://gristlabs.github.io/jupyterlite-widget/lab/index.html to test the changes in a Grist doc.
3. In the `grist-widget` repo, run `git submodule update --remote --init` to update the submodule to the latest commit in the `gh-pages` branch. Commit this update, push, and make a PR. The deploy preview URL can be used to test the changes.
4. Merge the `grist-widget` PR. This will trigger a deploy to production.

## Files

- `extension/` contains the JupyterLab extension that connects the Grist and JupyterLab APIs. See the [README there](./extension/README.md) for more details.
- `grist/` contains most of the Python code that runs inside the JupyterLite Pyodide and that users can call.
- `package.sh` packages the files under `grist` and puts them in `files/package.tar.gz`. JupyterLite picks up the contents of `files` when building, so the package can be downloaded from http://localhost:8000/files/package.tar.gz. `package.sh` is run by both `dev.sh` and the GitHub Action.
- `extension/src/initKernelPy.ts` contains the 'bootstrapping' Python code that the extension runs in the kernel on startup. It downloads the package, extracts it, and imports it.
- `dev.sh` cleans out old state, does some minimal building for development, and starts a local JupyterLite server.
- `jupyter-lite.json` contains configuration for the JupyterLite deployment.
