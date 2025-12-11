export enum Dialogs {
  UEDITOR_NEW_BRANCH = 1,
  UEDITOR_IMPORT_REMOTE_BRANCH,
  UEDITOR_DELETE_BRANCH,
  UEDITOR_MERGE_FROM_DEFAULT,

  FOLDER_CREATE,
  FOLDER_DELETE,
  FOLDER_RENAME,

  FILE_CREATE,
  FILE_DELETE,
  FILE_RENAME,
  FILE_REPLACE,
  FILE_UPLOAD,

  HELP_ABOUT,
}

export const appState: ApplicationState = $state({
  apiStatus: null,
  currentUser: null,
  currentBranch: null,
  currentFile: null,
  currentFileContent: null,
  activeDialog: null,
  branches: null,
  uEditionConfig: null,
  uEditorConfig: null,
  actions: [],
  tei: {
    blocks: [],
    marks: [],
  },
  ui: {
    hasLoggedOut: false,
    currentFileModified: false,
  },
});
