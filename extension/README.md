# grist_jupyterlab_widget

This is a JupyterLab extension that connects the Grist and JupyterLab APIs. It's tightly coupled with the JupyterLite deployment in this repo (the parent folder) and doesn't work on its own.

This folder was originally [its own repo](https://github.com/gristlabs/jupyterlab-widget-extension) generated using `copier` following the [extension tutorial](https://jupyterlab.readthedocs.io/en/stable/extension/extension_tutorial.html). This is the source of a lot of boilerplate configuration that probably isn't *all* needed but also probably shouldn't be messed with. Usually this extension would be published on PyPI (and maybe NPM) under the package name `grist_jupyterlab_widget`, but now the parent folder just installs it from the local filesystem.



### Development install

Below are some of the original instructions included with this repo which may be helpful.

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the grist_jupyterlab_widget directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall grist_jupyterlab_widget
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `grist-widget` within that folder.
