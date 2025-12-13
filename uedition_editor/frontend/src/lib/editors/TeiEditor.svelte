<script lang="ts">
  import { Tabs } from "bits-ui";

  import LoadingIndicator from "../LoadingIndicator.svelte";
  import TeiMetadataEditor from "./TeiMetadataEditor.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";
  import TeiTextListEditor from "./TeiTextListEditor.svelte";
  import { appState } from "../../state.svelte";
  import { runAction } from "../actions/util.svelte";

  const editorState: TEIEditorState = $state({
    sections: {},
    loaded: false,
    loading: false,
    loadError: false,
    loadedBranch: "",
    loadedFilename: "",
    currentTab: "",
    selectTextlistId: null,
    notifyModified() {
      const doc = [];
      for (let section of appState.uEditorConfig.tei.sections) {
        doc.push(editorState.sections[section.name]);
      }
      appState.currentFileContent = JSON.stringify(doc);
      appState.ui.currentFileModified = true;
    },
  });

  $effect(() => {
    if (appState.currentBranch !== null && appState.currentFile !== null) {
      if (
        !editorState.loading &&
        (editorState.loadedBranch !== appState.currentBranch.id ||
          editorState.loadedFilename !== appState.currentFile.fullpath)
      ) {
        editorState.loadedBranch = appState.currentBranch.id;
        editorState.loadedFilename = appState.currentFile.fullpath;
        loadNewFile();
      }
    } else {
      editorState.sections = {};
      editorState.loaded = false;
    }
  });

  function loadNewFile() {
    appState.currentFileContent = null;
    appState.ui.currentFileModified = false;
    editorState.loaded = false;
    editorState.loading = true;
    editorState.loadError = false;
    runAction({
      action: "LoadTextFile",
      branch: appState.currentBranch,
      filename: appState.currentFile.fullpath,
      callback: (data: string) => {
        try {
          appState.currentFileContent = data;
          const tmpDocument = JSON.parse(data);
          editorState.sections = {};
          editorState.currentTab = "";
          for (let section of appState.uEditorConfig.tei.sections) {
            if (editorState.currentTab === "") {
              editorState.currentTab = section.name;
            }
            for (let part of tmpDocument) {
              if (section.name === part.name) {
                part.type = section;
                editorState.sections[section.name] = part;
                break;
              }
            }
          }
          editorState.loading = false;
          editorState.loaded = true;
        } catch (e) {
          console.error(e);
          editorState.loading = false;
          editorState.loadError = true;
        }
      },
    });
  }

  function shortCutTracker(ev: KeyboardEvent) {
    if (
      appState.currentBranch !== null &&
      appState.currentFile !== null &&
      appState.currentFileContent !== null
    ) {
      if (ev.key === "s" && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        if (
          !appState.apiStatus?.git.protect_default_branch ||
          appState.apiStatus?.git.default_branch !== appState.currentBranch?.id
        ) {
          runAction({
            action: "SaveCurrentFile",
            branch: appState.currentBranch,
            filename: appState.currentFile.fullpath,
            data: appState.currentFileContent,
            callback() {
              appState.ui.currentFileModified = false;
            },
          });
        }
      }
    }
  }
</script>

<h1 class="sr-only">{appState.currentFile?.name}</h1>
{#if editorState.loaded}
  <div class="flex-1 flex overflow-hidden" onkeydown={shortCutTracker}>
    <Tabs.Root bind:value={editorState.currentTab} class="flex-1 flex flex-col">
      <Tabs.List>
        {#each appState.uEditorConfig?.tei.sections as section}
          <Tabs.Trigger value={section.name}>{section.title}</Tabs.Trigger>
        {/each}
      </Tabs.List>
      {#each appState.uEditorConfig?.tei.sections as section}
        <Tabs.Content value={section.name} class="flex-1 overflow-hidden">
          {#if section.type === "metadata"}
            <TeiMetadataEditor sectionName={section.name} {editorState} />
          {:else if section.type === "text"}
            <TeiTextEditor
              sectionName={section.name}
              sectionConfig={section}
              sectionContent={editorState.sections[section.name]}
              {editorState}
              jumpToTextlistDocument={(targetName, targetId) => {
                editorState.currentTab = targetName;
                editorState.selectTextlistId = targetId;
              }}
            />
          {:else if section.type === "textlist"}
            <TeiTextListEditor
              sectionName={section.name}
              sectionConfig={section}
              sectionContent={editorState.sections[section.name]}
              {editorState}
              jumpToTextlistDocument={(targetName, targetId) => {
                editorState.currentTab = targetName;
                editorState.selectTextlistId = targetId;
              }}
            />
          {/if}
        </Tabs.Content>
      {/each}
    </Tabs.Root>
  </div>
{:else if editorState.loadError}
  <p class=" px-4 py-2 text-red-800">
    There was an error loading this TEI file. The most likely cause is a TEI tag
    that is not configured. Please check your server logs for details.
  </p>
{:else}
  <LoadingIndicator>Loading the TEI file. Please wait...</LoadingIndicator>
{/if}
