import { ref, watch } from 'vue';
import type { UnwrapRef } from 'vue';

type SessionStorageObjectType = string | number | boolean | object;

// prevent prototype pollution attacks
export function parseJSON(input: string): any {
	if (String(input).includes('__proto__')) {
		return JSON.parse(input, noproto);
	}

	return JSON.parse(input);
}

export function noproto<T>(key: string, value: T): T | void {
	if (key !== '__proto__') {
		return value;
	}
}

export function useSessionStorage<T extends SessionStorageObjectType>(
	key: string,
	defaultValue: UnwrapRef<T> | null = null
) {
	const internalKey = `${key}`;
	const data = ref<T | null>(null);

	function getValue(): UnwrapRef<T> | null {
		const rawExistingValue = sessionStorage.getItem(internalKey);

		if (!rawExistingValue) return defaultValue;

		try {
			return parseJSON(rawExistingValue);
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn(`Couldn't parse value from local storage`, e);

			return defaultValue;
		}
	}

	function setValue(value: UnwrapRef<T> | null) {
		try {
			sessionStorage.setItem(internalKey, JSON.stringify(value));
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn(`Couldn't stringify and set value to local storage`, e);
		}
	}

	data.value = getValue();

	watch(data, () => {
		if (data.value == null) {
			sessionStorage.removeItem(internalKey);
		} else {
			setValue(data.value);
		}
	});

	return { data };
}