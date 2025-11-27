export const appState: ApplicationState = $state({
  apiStatus: null,
  currentUser: null,
  currentBranch: null,
  currentFile: null,
  currentFileContent: null,
  branches: null,
  uEditionConfig: null,
  uEditorConfig: null,
  tei: {
    blocks: [],
    marks: [],
  },
  ui: {
    hasLoggedOut: false,
    currentFileModified: false,
  }
});
