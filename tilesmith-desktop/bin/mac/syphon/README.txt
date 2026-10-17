MAC: Syphon output, built into TileSmith.
This folder already holds what TileSmith needs, so nothing has to be downloaded:
  bin/syphon.node                     node-syphon 1.5.5 (universal: Apple Silicon + Intel), MIT licence
                                      from the npm package node-syphon@1.5.5, file dist/bin/syphon.node
                                      SHA-256 911b0a472dca3de1ec7661a40cf66dd830b1d34382ac0761d14d3c7232daa047
  Frameworks/Syphon.framework         Syphon 5 (universal), BSD licence
                                      from https://github.com/benoitlahoz/node-syphon/releases (SyphonFramework.zip)
  Syphon-License.txt                  Syphon's licence. It must ship with the framework.
  node-syphon-License.txt             node-syphon's licence.
"npm run dist:mac" puts syphon.node in the app's Resources folder and Syphon.framework in its Frameworks folder,
and the "Start Syphon" button appears in the top bar.
Before building, scripts/check-share.js repairs the framework's internal shortcuts (symlinks) if unzipping
lost them, and clears the macOS download quarantine flag from this folder.
To build WITHOUT Syphon, delete this "syphon" folder; the Syphon button is then hidden.
Syphon: https://syphon.github.io   node-syphon: https://github.com/benoitlahoz/node-syphon
