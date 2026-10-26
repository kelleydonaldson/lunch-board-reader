You are reading a food truck's schedule graphic or event flyer.

The post carrying this image is dated: <POST_DATE as YYYY-MM-DD>, <WEEKDAY>

Return ONLY a JSON object in exactly this shape (no other text, no code fences):

{
  "truck": "<truck name exactly as printed>",
  "post_date": "<the post date above, YYYY-MM-DD>",
  "stops": [
    {
      "date": "<YYYY-MM-DD, or null>",
      "start": "<start time exactly as printed, e.g. \"11 AM\", or null>",
      "end": "<end time exactly as printed, or null>",
      "place": "<place/venue name exactly as printed, or null>",
      "address": "<street address exactly as printed, or null>"
    }
  ],
  "flags": [
    {
      "code": "<one of: UNREADABLE, NO_STREET_ADDRESS, FLYER_NOT_CONFIRMED, PRIVATE_STOP, WEEK_UNCLEAR>",
      "stop": <index of the stop in "stops" this flag is about, starting at 0, or null if the flag is not about a returned stop>,
      "field": "<the field this flag is about: date, start, end, place, or address; or null>",
      "note": "<one short sentence saying exactly what is unclear or why>"
    }
  ]
}

If there are no stops, "stops" is []. If there are no flags, "flags" is [].

Rules:
1. Weeks run Monday through Sunday. Anchor every weekday to the post
   date: a graphic that says "Mon-Fri" means the Monday-Friday of the
   Monday-Sunday week containing the post date. A weekday named in the
   graphic gets the date of that weekday in that week. If that date
   would fall BEFORE the post date, do not pick a week: write null for
   date and add a WEEK_UNCLEAR flag on that stop's date field.
2. Pair each time with its own stop. Never carry a time from one stop
   to another.
3. An event flyer counts as a stop ONLY if it clearly says this truck
   will be there on that date. Otherwise return no stop and add a
   FLYER_NOT_CONFIRMED flag (stop: null) saying why.
4. Anything unclear, smudged, or missing: write null for that field and
   add an UNREADABLE flag on that stop and field. NEVER invent a date,
   time, place, or address, and never complete an address from the
   place name alone.
5. A place with no street address stays plain text: address is null,
   with a NO_STREET_ADDRESS flag on that stop's address field. Do not
   guess one.
6. A stop outside the home town keeps its town and state in the address
   exactly as printed (e.g. "Henderson, KY").
7. A stop marked private or employees-only is not a public stop: return
   no stop for it and add a PRIVATE_STOP flag (stop: null) naming the
   place in the note.
