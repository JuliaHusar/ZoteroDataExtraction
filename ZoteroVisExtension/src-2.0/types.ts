export interface ApiOverride {
    id: string,
    version: string,
    rootURI: string,
    initialized: boolean,
    addedElementIDs: []

    init({id, version, rootURI}): void
    getTags(): object
    getLibraries(): object
}