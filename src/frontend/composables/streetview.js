const streetviewCache = {} // address -> Promise<string|null>

export function getStreetviewPhoto(address, lat, lng) {
	if (!(address in streetviewCache)) {
		streetviewCache[address] = fetch(`/api/streetview?lat=${lat}&lng=${lng}`)
			.then(res => res.ok ? res.json() : { photoUrl: null })
			.then(data => data.photoUrl)
			.catch(() => null)
	}
	return streetviewCache[address]
}

export function streetviewImageUrl(lat, lng, size) {
	return `/api/streetview/img?lat=${lat}&lng=${lng}&size=${size}`
}
