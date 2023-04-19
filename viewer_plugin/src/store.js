import { writable } from "svelte/store"

export const hasDataSrc = writable(false)

export const SIIBRA_API_ENDPOINT = `https://siibra-api-stable.apps.hbp.eu`
export const SIIBRA_JUGEX_ENDPOINT = ``

export const getGeneNames = async () => {
  const res = await fetch(`${SIIBRA_API_ENDPOINT}/v2_0/genes`).then()
  return await res.json()
}

export const parcellationId = "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290"
export const searchRegion = async input => {
  const url = new URL(`${SIIBRA_API_ENDPOINT}/v3_0/regions`)
  url.searchParams.set("parcellation_id", parcellationId)
  url.searchParams.set('find', input)
  const res = await fetch(url)
  const respJson = await res.json()
  return respJson.items
}
